from datetime import date

from ..extensions import db

NOMES_REFEICAO = ["Café da manhã", "Lanche da manhã", "Almoço", "Lanche da tarde",
                  "Pré-treino", "Pós-treino", "Jantar", "Ceia"]


class Refeicao(db.Model):
    __tablename__ = "refeicao"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    data = db.Column(db.Date, default=date.today, nullable=False)
    nome = db.Column(db.String(40), nullable=False)

    usuario = db.relationship("Usuario", back_populates="refeicoes")
    itens = db.relationship("ItemAlimentar", back_populates="refeicao", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Refeicao {self.nome} {self.data}>"


class ItemAlimentar(db.Model):
    __tablename__ = "item_alimentar"

    id = db.Column(db.Integer, primary_key=True)
    refeicao_id = db.Column(db.Integer, db.ForeignKey("refeicao.id"), nullable=False)
    alimento = db.Column(db.String(80), nullable=False)
    quantidade = db.Column(db.String(30))
    kcal = db.Column(db.Float, default=0)
    proteina_g = db.Column(db.Float, default=0)
    carboidrato_g = db.Column(db.Float, default=0)
    gordura_g = db.Column(db.Float, default=0)

    refeicao = db.relationship("Refeicao", back_populates="itens")

    def __repr__(self):
        return f"<ItemAlimentar {self.alimento}>"
