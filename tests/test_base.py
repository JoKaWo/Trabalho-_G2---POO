from datetime import date

from app.extensions import db
from app.models import Exercicio, GrupoMuscular, Serie, Treino, Usuario


def test_sem_login_vai_para_entrar(client):
    resposta = client.get("/treino/")
    assert resposta.status_code == 302
    assert "/entrar" in resposta.headers["Location"]


def test_cadastro_e_login(client):
    client.post("/cadastro", data={"nome": "Rogério", "email": "rogerio@email.com", "senha": "123456"})
    client.get("/sair")
    resposta = client.post("/entrar", data={"email": "rogerio@email.com", "senha": "123456"})
    assert resposta.status_code == 302


def test_senha_errada(client):
    client.post("/cadastro", data={"nome": "Rogério", "email": "rogerio@email.com", "senha": "123456"})
    client.get("/sair")
    resposta = client.post("/entrar", data={"email": "rogerio@email.com", "senha": "errada"})
    assert "E-mail ou senha incorretos".encode() in resposta.data


def test_todas_as_paginas_abrem(logado):
    paginas = [
        "/treino/", "/treino/registrar", "/treino/registrar/texto", "/treino/rotinas", "/treino/rotinas/nova",
        "/treino/exercicios", "/treino/historico",
        "/evolucao/", "/evolucao/exercicio",
        "/peso/", "/peso/historico",
        "/nutricao/", "/nutricao/diario", "/nutricao/ajuste",
    ]
    for pagina in paginas:
        assert logado.get(pagina).status_code == 200, pagina


def test_catalogo_de_exercicios(app):
    with app.app_context():
        assert db.session.query(GrupoMuscular).count() >= 10
        assert db.session.query(Exercicio).filter_by(nome="Supino reto").first() is not None


def test_relacionamentos_do_treino(app):
    with app.app_context():
        usuario = Usuario(nome="Teste", email="t@t.com")
        usuario.definir_senha("123456")
        supino = db.session.query(Exercicio).filter_by(nome="Supino reto").first()
        treino = Treino(usuario=usuario, data=date.today(), nome="Upper A", tipo="Upper")
        treino.series = [
            Serie(exercicio=supino, numero=1, carga_kg=60, repeticoes=10),
            Serie(exercicio=supino, numero=2, carga_kg=60, repeticoes=8),
        ]
        db.session.add(treino)
        db.session.commit()
        assert usuario.treinos[0].volume_total() == 1080
        assert len(supino.series) == 2
