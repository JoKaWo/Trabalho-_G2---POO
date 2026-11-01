import pytest

from app import create_app
from app.extensions import db
from config import TestConfig


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logado(client):
    client.post("/cadastro", data={"nome": "Antônio Silva", "email": "antonio@email.com", "senha": "123456"})
    return client
