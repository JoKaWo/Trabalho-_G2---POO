from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("treino", __name__, url_prefix="/treino")

OPCOES = [
    ("treino.index", "Hoje"),
    ("treino.registrar", "Registrar"),
    ("treino.rotinas", "Rotinas"),
    ("treino.exercicios", "Exercícios"),
    ("treino.historico", "Histórico"),
]


@bp.context_processor
def opcoes_da_aba():
    return {"aba": "Treino", "opcoes": OPCOES}


@bp.route("/")
@login_required
def index():
    return render_template("treino/hoje.html")


@bp.route("/registrar")
@login_required
def registrar():
    return render_template("treino/registrar.html")


@bp.route("/rotinas")
@login_required
def rotinas():
    return render_template("treino/rotinas.html")


@bp.route("/exercicios")
@login_required
def exercicios():
    return render_template("treino/exercicios.html")


@bp.route("/historico")
@login_required
def historico():
    return render_template("treino/historico.html")


@bp.route("/rotinas/nova")
@login_required
def nova_rotina():
    return render_template("treino/nova_rotina.html", ativo="treino.rotinas")


@bp.route("/registrar/texto")
@login_required
def texto():
    return render_template("treino/texto.html", ativo="treino.registrar")
