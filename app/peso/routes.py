from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import MetaPeso, RegistroPeso
from ..models.usuario import FASES
from .calculos import AnalisePeso, GraficoPeso, formatar_numero
from .validacao import ler_data, ler_numero, peso_valido

bp = Blueprint("peso", __name__, url_prefix="/peso")

OPCOES = [
    ("peso.index", "Meta"),
    ("peso.historico", "Histórico"),
]

# Deixa usar {{ valor|numero(1) }} nos templates para escrever 87.6 como 87,6
bp.add_app_template_filter(formatar_numero, "numero")


@bp.context_processor
def opcoes_da_aba():
    return {"aba": "Peso", "opcoes": OPCOES}


@bp.route("/")
@login_required
def index():
    return render_template(
        "peso/meta.html",
        analise=AnalisePeso(current_user.registros_peso),
        meta=current_user.meta_ativa,
        fases=FASES,
        hoje=date.today(),
    )


@bp.route("/registrar", methods=["POST"])
@login_required
def registrar():
    peso = ler_numero(request.form.get("peso"))
    texto_data = request.form.get("data", "").strip()
    data = ler_data(texto_data) if texto_data else date.today()

    if not peso_valido(peso):
        flash("Digite um peso válido, entre 20 e 400 kg.", "erro")
    elif data is None or data > date.today():
        flash("Escolha uma data válida que não seja no futuro.", "erro")
    else:
        # Se já existe pesagem nesse dia, atualiza em vez de criar outra
        registro = RegistroPeso.query.filter_by(usuario_id=current_user.id, data=data).first()
        if registro:
            registro.peso_kg = peso
            flash("Pesagem desse dia atualizada.", "ok")
        else:
            db.session.add(RegistroPeso(usuario_id=current_user.id, data=data, peso_kg=peso))
            flash("Peso registrado.", "ok")
        db.session.commit()
    return redirect(url_for("peso.index"))


@bp.route("/meta", methods=["POST"])
@login_required
def salvar_meta():
    fase = request.form.get("fase")
    texto_peso = request.form.get("peso_meta", "").strip()
    texto_data = request.form.get("data_limite", "").strip()

    nova_meta = None
    if texto_peso or texto_data:  # se os dois campos estiverem vazios, só a fase é salva
        peso_meta = ler_numero(texto_peso)
        data_limite = ler_data(texto_data)
        if not peso_valido(peso_meta):
            flash("Digite um peso de meta válido, entre 20 e 400 kg.", "erro")
            return redirect(url_for("peso.index"))
        if data_limite is None or data_limite <= date.today():
            flash("Escolha uma data limite depois de hoje.", "erro")
            return redirect(url_for("peso.index"))
        nova_meta = MetaPeso(usuario_id=current_user.id, peso_meta_kg=peso_meta, data_limite=data_limite, ativa=True)

    if fase in FASES:
        current_user.fase = fase
    if nova_meta:
        for meta_antiga in current_user.metas:  # só uma meta fica ativa por vez
            meta_antiga.ativa = False
        db.session.add(nova_meta)
    db.session.commit()
    flash("Fase e meta salvas.", "ok")
    return redirect(url_for("peso.index"))


@bp.route("/historico")
@login_required
def historico():
    registros = current_user.registros_peso
    meta = current_user.meta_ativa
    return render_template(
        "peso/historico.html",
        analise=AnalisePeso(registros),
        grafico=GraficoPeso(registros, meta.peso_meta_kg if meta else None),
        meta=meta,
    )


@bp.route("/historico/<int:registro_id>/excluir", methods=["POST"])
@login_required
def excluir(registro_id):
    # Filtra também pelo usuário: ninguém consegue apagar a pesagem de outra pessoa
    registro = RegistroPeso.query.filter_by(id=registro_id, usuario_id=current_user.id).first_or_404()
    db.session.delete(registro)
    db.session.commit()
    flash("Pesagem excluída.", "ok")
    return redirect(url_for("peso.historico"))
