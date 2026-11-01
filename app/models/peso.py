from datetime import date

from ..extensions import db


class MetaPeso(db.Model):
    __tablename__ = "meta_peso"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    peso_meta_kg = db.Column(db.Float, nullable=False)
    data_limite = db.Column(db.Date, nullable=False)
    ativa = db.Column(db.Boolean, default=True)

    usuario = db.relationship("Usuario", back_populates="metas")

    def __repr__(self):
        return f"<MetaPeso {self.peso_meta_kg} kg até {self.data_limite}>"


class RegistroPeso(db.Model):
    __tablename__ = "registro_peso"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    data = db.Column(db.Date, default=date.today, nullable=False)
    peso_kg = db.Column(db.Float, nullable=False)

    usuario = db.relationship("Usuario", back_populates="registros_peso")

    def __repr__(self):
        return f"<RegistroPeso {self.data}: {self.peso_kg} kg>"
