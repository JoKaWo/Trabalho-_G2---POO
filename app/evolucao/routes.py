from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("evolucao", __name__, url_prefix="/evolucao")

OPCOES = [
    ("evolucao.index", "Resumo"),
    ("evolucao.exercicio", "Por exercício"),
]


@bp.context_processor
def opcoes_da_aba():
    return {"aba": "Evolução", "opcoes": OPCOES}


@bp.route("/")
@login_required
def index():
    return render_template("evolucao/resumo.html")


@bp.route("/exercicio")
@login_required
def exercicio():
    return render_template("evolucao/exercicio.html")
