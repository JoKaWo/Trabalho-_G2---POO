from .extensions import db
from .models import Exercicio, GrupoMuscular

CATALOGO = {
    "Peito": [("Supino reto", "Barra"), ("Supino inclinado com halteres", "Halter"), ("Crucifixo máquina", "Máquina"), ("Peck deck", "Máquina"), ("Crossover", "Cabo")],
    "Costas": [("Puxada frontal", "Máquina"), ("Remada baixa", "Cabo"), ("Remada curvada", "Barra"), ("Pulldown", "Cabo"), ("Barra fixa", "Peso corporal")],
    "Ombros": [("Desenvolvimento com halteres", "Halter"), ("Elevação lateral", "Halter"), ("Crucifixo inverso", "Máquina")],
    "Bíceps": [("Rosca direta", "Barra"), ("Rosca martelo", "Halter"), ("Rosca Scott", "Máquina")],
    "Tríceps": [("Tríceps corda", "Cabo"), ("Tríceps testa", "Barra"), ("Paralelas", "Peso corporal")],
    "Quadríceps": [("Agachamento livre", "Barra"), ("Leg press 45°", "Máquina"), ("Cadeira extensora", "Máquina"), ("Hack machine", "Máquina")],
    "Posterior": [("Mesa flexora", "Máquina"), ("Cadeira flexora", "Máquina"), ("Stiff", "Barra"), ("Levantamento terra", "Barra")],
    "Glúteos": [("Elevação pélvica", "Barra"), ("Cadeira abdutora", "Máquina")],
    "Panturrilha": [("Panturrilha em pé", "Máquina"), ("Panturrilha sentado", "Máquina")],
    "Abdômen": [("Abdominal máquina", "Máquina"), ("Prancha", "Peso corporal")],
}


def popular_catalogo():
    if db.session.query(GrupoMuscular).first():
        return
    for nome_grupo, exercicios in CATALOGO.items():
        grupo = GrupoMuscular(nome=nome_grupo)
        db.session.add(grupo)
        for nome, equipamento in exercicios:
            db.session.add(Exercicio(nome=nome, equipamento=equipamento, grupo=grupo))
    db.session.commit()
