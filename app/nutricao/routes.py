from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("nutricao", __name__, url_prefix="/nutricao")

OPCOES = [
    ("nutricao.index", "Metas"),
    ("nutricao.diario", "Diário"),
    ("nutricao.ajuste", "Ajuste com IA"),
]


@bp.context_processor
def opcoes_da_aba():
    return {"aba": "Nutrição", "opcoes": OPCOES}


@bp.route("/")
@login_required
def index():
    return render_template("nutricao/metas.html")


@bp.route("/diario")
@login_required
def diario():
    return render_template("nutricao/diario.html")


@bp.route("/ajuste")
@login_required
def ajuste():
    return render_template("nutricao/ajuste.html")
