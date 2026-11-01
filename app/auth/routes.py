from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..models import Usuario

bp = Blueprint("auth", __name__)


@bp.route("/entrar", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.inicio"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.verificar_senha(senha):
            login_user(usuario, remember=bool(request.form.get("lembrar")))
            return redirect(request.args.get("next") or url_for("main.inicio"))
        flash("E-mail ou senha incorretos.", "erro")
    return render_template("auth/login.html")


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("main.inicio"))
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        if not nome or not email or len(senha) < 6:
            flash("Preencha nome, e-mail e uma senha com pelo menos 6 caracteres.", "erro")
        elif Usuario.query.filter_by(email=email).first():
            flash("Já existe uma conta com esse e-mail. Entre com ela.", "erro")
        else:
            usuario = Usuario(nome=nome, email=email)
            usuario.definir_senha(senha)
            db.session.add(usuario)
            db.session.commit()
            login_user(usuario)
            flash("Conta criada.", "ok")
            return redirect(url_for("main.inicio"))
    return render_template("auth/cadastro.html")


@bp.route("/sair")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
