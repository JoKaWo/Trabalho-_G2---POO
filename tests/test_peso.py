from datetime import date, timedelta
from types import SimpleNamespace

from app.extensions import db
from app.models import MetaPeso, RegistroPeso, Usuario
from app.peso.calculos import AnalisePeso, GraficoPeso, formatar_numero
from app.peso.validacao import ler_data, ler_numero, peso_valido

HOJE = date(2026, 10, 22)


def pesagens(*itens):
    """Cria pesagens de mentira: cada item é (dias atrás, peso)."""
    return [SimpleNamespace(data=HOJE - timedelta(days=dias), peso_kg=peso) for dias, peso in itens]


# ---------- funções de leitura ----------
def test_ler_numero_aceita_virgula_e_ponto():
    assert ler_numero("87,9") == 87.9
    assert ler_numero(" 87.9 ") == 87.9
    assert ler_numero("abc") is None
    assert ler_numero(None) is None


def test_peso_valido():
    assert peso_valido(87.9)
    assert not peso_valido(5)
    assert not peso_valido(900)
    assert not peso_valido(None)


def test_ler_data():
    assert ler_data("2026-10-22") == date(2026, 10, 22)
    assert ler_data("22/10/2026") is None


def test_formatar_numero():
    assert formatar_numero(87.6) == "87,6"
    assert formatar_numero(-1.84, 1, True) == "-1,8"
    assert formatar_numero(0.8, 1, True) == "+0,8"
    assert formatar_numero(-0.02, 1, True) == "0,0"
    assert formatar_numero(None) == "–"


# ---------- cálculos ----------
def test_peso_atual_e_variacao_total():
    analise = AnalisePeso(pesagens((10, 90.0), (0, 88.0), (5, 89.0)), hoje=HOJE)
    assert analise.peso_atual == 88.0
    assert analise.variacao_total() == -2.0


def test_sem_pesagens():
    analise = AnalisePeso([], hoje=HOJE)
    assert not analise.tem_registros
    assert analise.peso_atual is None
    assert analise.variacao_total() is None
    assert analise.media_ultimos_dias() is None
    assert analise.ritmo_semanal() is None


def test_media_dos_ultimos_7_dias():
    analise = AnalisePeso(pesagens((20, 95.0), (6, 90.0), (0, 88.0)), hoje=HOJE)
    assert analise.media_ultimos_dias(7) == 89.0  # a pesagem de 20 dias atrás fica de fora


def test_ritmo_semanal():
    analise = AnalisePeso(pesagens((14, 90.0), (0, 88.0)), hoje=HOJE)
    assert analise.ritmo_semanal() == -1.0  # perdeu 2 kg em 2 semanas


def test_ritmo_precisa_de_7_dias():
    analise = AnalisePeso(pesagens((3, 90.0), (0, 88.0)), hoje=HOJE)
    assert analise.ritmo_semanal() is None


def test_projecao_dentro_do_prazo():
    meta = SimpleNamespace(peso_meta_kg=80.0, data_limite=HOJE + timedelta(days=100))
    analise = AnalisePeso(pesagens((14, 90.0), (0, 88.0)), hoje=HOJE)  # -1 kg por semana
    assert analise.data_prevista(meta) == HOJE + timedelta(days=56)  # faltam 8 kg = 8 semanas
    texto, situacao = analise.mensagem_projecao(meta)
    assert situacao == "bom"
    assert "dentro do prazo" in texto


def test_projecao_depois_do_prazo():
    meta = SimpleNamespace(peso_meta_kg=80.0, data_limite=HOJE + timedelta(days=30))
    analise = AnalisePeso(pesagens((14, 90.0), (0, 88.0)), hoje=HOJE)
    texto, situacao = analise.mensagem_projecao(meta)
    assert situacao == "alerta"
    assert "depois do prazo" in texto


def test_projecao_direcao_errada():
    meta = SimpleNamespace(peso_meta_kg=80.0, data_limite=HOJE + timedelta(days=100))
    analise = AnalisePeso(pesagens((14, 86.0), (0, 88.0)), hoje=HOJE)  # engordando, meta é emagrecer
    assert analise.data_prevista(meta) is None
    assert analise.mensagem_projecao(meta)[1] == "alerta"


def test_ritmo_necessario():
    meta = SimpleNamespace(peso_meta_kg=80.0, data_limite=HOJE + timedelta(days=56))
    analise = AnalisePeso(pesagens((0, 88.0)), hoje=HOJE)
    assert analise.ritmo_necessario(meta) == -1.0


def test_linhas_do_historico_vem_da_mais_nova_para_a_mais_antiga():
    analise = AnalisePeso(pesagens((4, 90.0), (2, 89.0), (0, 88.5)), hoje=HOJE)
    linhas = analise.linhas_do_historico()
    assert [l[0].peso_kg for l in linhas] == [88.5, 89.0, 90.0]
    assert [l[1] for l in linhas] == [-0.5, -1.0, None]


# ---------- gráfico ----------
def test_grafico_posicoes():
    grafico = GraficoPeso(pesagens((10, 90.0), (0, 88.0)), peso_meta=85.0)
    primeiro, ultimo = grafico.pontos
    assert primeiro["x"] == grafico.ESQUERDA  # data mais antiga na esquerda
    assert ultimo["x"] == grafico.LARGURA - grafico.DIREITA  # data mais nova na direita
    assert primeiro["y"] < ultimo["y"]  # peso maior fica mais para cima (y menor)
    assert grafico.y_meta > ultimo["y"]  # a meta (85) está abaixo do último peso (88)
    assert grafico.minimo <= 85 and grafico.maximo >= 90


def test_grafico_com_um_ponto_nao_quebra():
    grafico = GraficoPeso(pesagens((0, 88.0)))
    assert len(grafico.pontos) == 1
    assert grafico.y_meta is None


# ---------- páginas e banco ----------
def test_registrar_peso(logado, app):
    resposta = logado.post("/peso/registrar", data={"peso": "87,9", "data": date.today().isoformat()})
    assert resposta.status_code == 302
    with app.app_context():
        registros = db.session.query(RegistroPeso).all()
        assert len(registros) == 1
        assert registros[0].peso_kg == 87.9
    assert "87,9".encode() in logado.get("/peso/").data


def test_registrar_no_mesmo_dia_atualiza(logado, app):
    hoje = date.today().isoformat()
    logado.post("/peso/registrar", data={"peso": "88", "data": hoje})
    logado.post("/peso/registrar", data={"peso": "87,5", "data": hoje})
    with app.app_context():
        registros = db.session.query(RegistroPeso).all()
        assert len(registros) == 1
        assert registros[0].peso_kg == 87.5


def test_peso_invalido_nao_salva(logado, app):
    logado.post("/peso/registrar", data={"peso": "abc", "data": date.today().isoformat()})
    logado.post("/peso/registrar", data={"peso": "900", "data": date.today().isoformat()})
    amanha = (date.today() + timedelta(days=1)).isoformat()
    logado.post("/peso/registrar", data={"peso": "80", "data": amanha})
    with app.app_context():
        assert db.session.query(RegistroPeso).count() == 0


def test_salvar_fase_e_meta(logado, app):
    limite = (date.today() + timedelta(days=90)).isoformat()
    logado.post("/peso/meta", data={"fase": "cut", "peso_meta": "80", "data_limite": limite})
    logado.post("/peso/meta", data={"fase": "cut", "peso_meta": "78,5", "data_limite": limite})
    with app.app_context():
        usuario = db.session.query(Usuario).first()
        assert usuario.fase == "cut"
        assert db.session.query(MetaPeso).count() == 2
        assert usuario.meta_ativa.peso_meta_kg == 78.5  # só a última meta fica ativa
        assert sum(1 for m in usuario.metas if m.ativa) == 1


def test_meta_com_data_no_passado_nao_salva(logado, app):
    ontem = (date.today() - timedelta(days=1)).isoformat()
    logado.post("/peso/meta", data={"fase": "bulk", "peso_meta": "80", "data_limite": ontem})
    with app.app_context():
        assert db.session.query(MetaPeso).count() == 0
        assert db.session.query(Usuario).first().fase == "manutencao"  # a fase também não mudou


def test_historico_e_excluir(logado, app):
    for dias, peso in [(3, "90"), (2, "89,5"), (0, "89")]:
        data = (date.today() - timedelta(days=dias)).isoformat()
        logado.post("/peso/registrar", data={"peso": peso, "data": data})
    pagina = logado.get("/peso/historico").data
    assert b"<svg" in pagina  # com 2 ou mais pesagens aparece o gráfico
    with app.app_context():
        registro_id = db.session.query(RegistroPeso).first().id
    logado.post(f"/peso/historico/{registro_id}/excluir")
    with app.app_context():
        assert db.session.query(RegistroPeso).count() == 2


def test_nao_exclui_pesagem_de_outro_usuario(logado, app):
    with app.app_context():
        outro = Usuario(nome="Outro", email="outro@email.com")
        outro.definir_senha("123456")
        db.session.add(outro)
        db.session.flush()
        registro = RegistroPeso(usuario_id=outro.id, data=date.today(), peso_kg=70)
        db.session.add(registro)
        db.session.commit()
        registro_id = registro.id
    assert logado.post(f"/peso/historico/{registro_id}/excluir").status_code == 404
    with app.app_context():
        assert db.session.query(RegistroPeso).count() == 1
