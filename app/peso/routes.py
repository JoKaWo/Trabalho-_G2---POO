from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("peso", __name__, url_prefix="/peso")

OPCOES = [
    ("peso.index", "Meta"),
    ("peso.historico", "Histórico"),
]


@bp.context_processor
def opcoes_da_aba():
    return {"aba": "Peso", "opcoes": OPCOES}


@bp.route("/")
@login_required
def index():
    return render_template("peso/meta.html")


@bp.route("/historico")
@login_required
def historico():
    return render_template("peso/historico.html")
