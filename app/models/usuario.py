from datetime import date, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db, login_manager

FASES = {"cut": "Cutting", "bulk": "Bulking", "manutencao": "Manutenção"}
NIVEIS_ATIVIDADE = {
    1.2: "Sedentário",
    1.375: "Leve (1 a 3 treinos por semana)",
    1.55: "Moderado (3 a 5 treinos por semana)",
    1.725: "Alto (6 a 7 treinos por semana)",
    1.9: "Muito alto (treino pesado e trabalho físico)",
}


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(256), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.now)

    sexo = db.Column(db.String(1))
    data_nascimento = db.Column(db.Date)
    altura_cm = db.Column(db.Float)
    nivel_atividade = db.Column(db.Float, default=1.55)
    fase = db.Column(db.String(20), default="manutencao")
    prioridade = db.Column(db.String(30))

    metas = db.relationship("MetaPeso", back_populates="usuario", cascade="all, delete-orphan")
    registros_peso = db.relationship("RegistroPeso", back_populates="usuario", cascade="all, delete-orphan",
                                     order_by="RegistroPeso.data")
    rotinas = db.relationship("Rotina", back_populates="usuario", cascade="all, delete-orphan")
    treinos = db.relationship("Treino", back_populates="usuario", cascade="all, delete-orphan",
                              order_by="Treino.data.desc()")
    refeicoes = db.relationship("Refeicao", back_populates="usuario", cascade="all, delete-orphan")
    exercicios_proprios = db.relationship("Exercicio", back_populates="usuario")

    def definir_senha(self, senha: str) -> None:
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)

    @property
    def idade(self):
        if not self.data_nascimento:
            return None
        hoje = date.today()
        n = self.data_nascimento
        return hoje.year - n.year - ((hoje.month, hoje.day) < (n.month, n.day))

    @property
    def peso_atual(self):
        return self.registros_peso[-1].peso_kg if self.registros_peso else None

    @property
    def meta_ativa(self):
        return next((m for m in self.metas if m.ativa), None)

    def __repr__(self):
        return f"<Usuario {self.email}>"


@login_manager.user_loader
def carregar_usuario(usuario_id):
    return db.session.get(Usuario, int(usuario_id))
