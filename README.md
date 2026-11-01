# Ficha de Academia

Aplicativo web para registrar treinos, acompanhar a progressão de carga, o peso corporal e a alimentação.
Trabalho de G2 de Programação Orientada a Objeto.

Equipe: Elisa Diefenthäler Jost, Josué Kaufmann Wolfgramm, Pedro Kahl Pereira e Vitor Jachini de Lima.

**Tecnologias:** Python 3.10+, Flask (interface web), SQLite com Flask-SQLAlchemy (persistência), Flask-Login (login).

## Como rodar

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
python run.py
```

Abra http://127.0.0.1:5000, crie uma conta e entre.
O banco `instance/ficha.db` é criado sozinho na primeira execução, já com um catálogo de grupos musculares e exercícios.
Para começar do zero, apague esse arquivo.

## O que já tem

- Cadastro, login e logout
- Layout com as abas Treino, Evolução, Peso e Nutrição (ainda vazias)
- As classes do banco em `app/models/`, seguindo o DER do trabalho
- Testes básicos em `tests/` (rode com `pytest`)

## Estrutura

```
app/
  __init__.py          cria o app, registra as abas e o banco
  extensions.py        db (SQLAlchemy) e login_manager
  seed.py              catálogo inicial de exercícios
  models/              classes do banco
    usuario.py         Usuario
    treino.py          GrupoMuscular, Exercicio, Rotina, RotinaDia, RotinaExercicio, Treino, Serie
    peso.py            MetaPeso, RegistroPeso
    nutricao.py        Refeicao, ItemAlimentar
  auth/                login e cadastro
  treino/  evolucao/  peso/  nutricao/   rotas de cada aba
  templates/           páginas HTML (base.html é o layout comum)
  static/css/style.css estilos e cores
tests/                 testes
```

## Dicas rápidas

- O usuário logado está em `current_user` (ex.: `current_user.treinos`, `current_user.registros_peso`).
- Para salvar no banco: `db.session.add(objeto)` e depois `db.session.commit()`.
- Se alguma classe em `app/models/` mudar, apague o `instance/ficha.db` local para o banco ser recriado.
