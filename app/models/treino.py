from datetime import date

from ..extensions import db

DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
TIPOS_TREINO = ["Upper", "Lower", "Push", "Pull", "Legs", "Full body", "Outro"]


class GrupoMuscular(db.Model):
    __tablename__ = "grupo_muscular"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), unique=True, nullable=False)

    exercicios = db.relationship("Exercicio", back_populates="grupo")

    def __repr__(self):
        return f"<GrupoMuscular {self.nome}>"


class Exercicio(db.Model):
    __tablename__ = "exercicio"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    equipamento = db.Column(db.String(40))
    grupo_id = db.Column(db.Integer, db.ForeignKey("grupo_muscular.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))  # vazio = exercício do catálogo

    grupo = db.relationship("GrupoMuscular", back_populates="exercicios")
    usuario = db.relationship("Usuario", back_populates="exercicios_proprios")
    series = db.relationship("Serie", back_populates="exercicio")

    def __repr__(self):
        return f"<Exercicio {self.nome}>"


class Rotina(db.Model):
    __tablename__ = "rotina"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    nome = db.Column(db.String(60), nullable=False)
    tipo = db.Column(db.String(30), default="Outro")

    usuario = db.relationship("Usuario", back_populates="rotinas")
    dias = db.relationship("RotinaDia", back_populates="rotina", cascade="all, delete-orphan")
    itens = db.relationship("RotinaExercicio", back_populates="rotina", cascade="all, delete-orphan",
                            order_by="RotinaExercicio.ordem")
    treinos = db.relationship("Treino", back_populates="rotina")

    @property
    def nomes_dos_dias(self):
        return [DIAS_SEMANA[d.dia_semana] for d in sorted(self.dias, key=lambda d: d.dia_semana)]

    def __repr__(self):
        return f"<Rotina {self.nome}>"


class RotinaDia(db.Model):
    __tablename__ = "rotina_dia"

    rotina_id = db.Column(db.Integer, db.ForeignKey("rotina.id"), primary_key=True)
    dia_semana = db.Column(db.Integer, primary_key=True)  # 0 = segunda ... 6 = domingo

    rotina = db.relationship("Rotina", back_populates="dias")


class RotinaExercicio(db.Model):
    __tablename__ = "rotina_exercicio"

    rotina_id = db.Column(db.Integer, db.ForeignKey("rotina.id"), primary_key=True)
    exercicio_id = db.Column(db.Integer, db.ForeignKey("exercicio.id"), primary_key=True)
    ordem = db.Column(db.Integer, default=1)
    series_alvo = db.Column(db.Integer, default=3)
    reps_min = db.Column(db.Integer, default=8)
    reps_max = db.Column(db.Integer, default=12)

    rotina = db.relationship("Rotina", back_populates="itens")
    exercicio = db.relationship("Exercicio")


class Treino(db.Model):
    __tablename__ = "treino"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    rotina_id = db.Column(db.Integer, db.ForeignKey("rotina.id"))  # vazio = treino livre
    data = db.Column(db.Date, default=date.today, nullable=False)
    nome = db.Column(db.String(60))
    tipo = db.Column(db.String(30))

    usuario = db.relationship("Usuario", back_populates="treinos")
    rotina = db.relationship("Rotina", back_populates="treinos")
    series = db.relationship("Serie", back_populates="treino", cascade="all, delete-orphan",
                             order_by="Serie.numero")

    def volume_total(self) -> float:
        return sum(s.volume() for s in self.series)

    def __repr__(self):
        return f"<Treino {self.nome} {self.data}>"


class Serie(db.Model):
    __tablename__ = "serie"

    id = db.Column(db.Integer, primary_key=True)
    treino_id = db.Column(db.Integer, db.ForeignKey("treino.id"), nullable=False)
    exercicio_id = db.Column(db.Integer, db.ForeignKey("exercicio.id"), nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    carga_kg = db.Column(db.Float, default=0)
    repeticoes = db.Column(db.Integer, nullable=False)

    treino = db.relationship("Treino", back_populates="series")
    exercicio = db.relationship("Exercicio", back_populates="series")

    def volume(self) -> float:
        return (self.carga_kg or 0) * self.repeticoes


    def __repr__(self):
        return f"<Serie {self.numero}: {self.carga_kg} kg x {self.repeticoes}>"
