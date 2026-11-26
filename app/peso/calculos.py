"""Cálculos e gráfico da aba Peso.

Nada aqui mexe no banco de dados nem no Flask. As classes só recebem uma lista de
pesagens (qualquer objeto que tenha os atributos `data` e `peso_kg`, como o
RegistroPeso) e devolvem números e textos. Isso deixa o código simples de testar
e de explicar.
"""
from datetime import date, timedelta
from math import ceil, floor


def formatar_numero(valor, casas=1, com_sinal=False):
    """Escreve o número como no Brasil: 87.6 vira '87,6'. Sem valor, devolve um traço."""
    if valor is None:
        return "–"
    valor = round(valor, casas)
    if valor == 0:
        valor = 0.0  # evita aparecer "-0,0"
    texto = f"{valor:.{casas}f}".replace(".", ",")
    if com_sinal and valor > 0:
        texto = "+" + texto
    return texto


class AnalisePeso:
    """Estatísticas e projeção de meta a partir das pesagens do usuário."""

    def __init__(self, registros, hoje=None):
        self.registros = sorted(registros, key=lambda r: r.data)  # da mais antiga para a mais nova
        self.hoje = hoje or date.today()

    # ---------- dados básicos ----------
    @property
    def tem_registros(self):
        return len(self.registros) > 0

    @property
    def peso_atual(self):
        return self.registros[-1].peso_kg if self.registros else None

    @property
    def data_atual(self):
        return self.registros[-1].data if self.registros else None

    def variacao_total(self):
        """Quanto o peso mudou desde a primeira pesagem (negativo = emagreceu)."""
        if len(self.registros) < 2:
            return None
        return self.registros[-1].peso_kg - self.registros[0].peso_kg

    def media_ultimos_dias(self, dias=7):
        """Média das pesagens dos últimos `dias` dias (contando hoje)."""
        desde = self.hoje - timedelta(days=dias - 1)
        pesos = [r.peso_kg for r in self.registros if r.data >= desde]
        if not pesos:
            return None
        return sum(pesos) / len(pesos)

    # ---------- ritmo e projeção ----------
    def ritmo_semanal(self, dias=28):
        """Quantos kg o usuário está ganhando (+) ou perdendo (-) por semana.

        Usa a primeira e a última pesagem dos últimos `dias` dias. Precisa de pelo
        menos 7 dias entre elas, senão a oscilação normal do peso engana.
        """
        desde = self.hoje - timedelta(days=dias)
        recentes = [r for r in self.registros if r.data >= desde]
        if len(recentes) < 2:
            return None
        primeiro, ultimo = recentes[0], recentes[-1]
        intervalo = (ultimo.data - primeiro.data).days
        if intervalo < 7:
            return None
        return (ultimo.peso_kg - primeiro.peso_kg) / intervalo * 7

    def ritmo_necessario(self, meta):
        """Quantos kg por semana seria preciso variar para bater a meta no prazo."""
        dias_restantes = (meta.data_limite - self.hoje).days
        if self.peso_atual is None or dias_restantes <= 0:
            return None
        return (meta.peso_meta_kg - self.peso_atual) / dias_restantes * 7

    def data_prevista(self, meta):
        """Data em que a meta seria batida se o ritmo atual continuar (ou None)."""
        ritmo = self.ritmo_semanal()
        if self.peso_atual is None or not ritmo:
            return None
        semanas = (meta.peso_meta_kg - self.peso_atual) / ritmo
        if semanas < 0:  # está indo na direção contrária da meta
            return None
        return self.hoje + timedelta(days=round(semanas * 7))

    def mensagem_projecao(self, meta):
        """Devolve (texto, situacao). A situacao é 'bom', 'alerta' ou 'neutro' e escolhe a cor do texto."""
        if self.peso_atual is None:
            return "Registre seu peso para ver a projeção da meta.", "neutro"
        if abs(self.peso_atual - meta.peso_meta_kg) < 0.05:
            return "Você já está no peso da meta.", "bom"
        if self.ritmo_semanal() is None:
            return "Registre seu peso ao longo de pelo menos 7 dias para calcular o seu ritmo.", "neutro"

        previsto = self.data_prevista(meta)
        if previsto is None:
            return "No ritmo atual você não está indo em direção à meta.", "alerta"
        data_texto = previsto.strftime("%d/%m/%Y")
        if previsto <= meta.data_limite:
            return f"No ritmo atual você bate a meta por volta de {data_texto}, dentro do prazo.", "bom"
        limite_texto = meta.data_limite.strftime("%d/%m/%Y")
        return f"No ritmo atual você só chega na meta por volta de {data_texto}, depois do prazo ({limite_texto}).", "alerta"

    # ---------- lista do histórico ----------
    def linhas_do_historico(self):
        """Lista de (pesagem, variação desde a pesagem anterior), da mais nova para a mais antiga."""
        linhas = []
        for i in range(len(self.registros) - 1, -1, -1):
            variacao = None
            if i > 0:
                variacao = self.registros[i].peso_kg - self.registros[i - 1].peso_kg
            linhas.append((self.registros[i], variacao))
        return linhas


class GraficoPeso:
    """Calcula as posições para desenhar o gráfico de linha do peso em SVG.

    O template só pega os números prontos daqui e desenha. Nenhuma biblioteca de gráfico é usada.
    """

    LARGURA = 600
    ALTURA = 240
    ESQUERDA = 44
    DIREITA = 16
    TOPO = 16
    BASE = 30

    def __init__(self, registros, peso_meta=None):
        self.registros = sorted(registros, key=lambda r: r.data)
        self.peso_meta = peso_meta
        pesos = [r.peso_kg for r in self.registros]
        if peso_meta is not None:
            pesos.append(peso_meta)
        if pesos:
            # arredonda para fora e dá 1 kg de folga em cima e embaixo
            self.minimo = floor(min(pesos)) - 1
            self.maximo = ceil(max(pesos)) + 1
        else:
            self.minimo, self.maximo = 0, 1

    @property
    def largura_util(self):
        return self.LARGURA - self.ESQUERDA - self.DIREITA

    @property
    def altura_util(self):
        return self.ALTURA - self.TOPO - self.BASE

    @property
    def base_y(self):
        """Altura (y) onde fica o eixo de baixo."""
        return self.TOPO + self.altura_util

    def _x(self, data):
        """Posição horizontal: a primeira data fica na esquerda e a última na direita."""
        primeira = self.registros[0].data
        ultima = self.registros[-1].data
        total_dias = (ultima - primeira).days
        if total_dias == 0:
            return self.ESQUERDA + self.largura_util / 2
        return self.ESQUERDA + (data - primeira).days / total_dias * self.largura_util

    def _y(self, peso):
        """Posição vertical: peso maior fica mais para cima (no SVG o y cresce para baixo)."""
        proporcao = (peso - self.minimo) / (self.maximo - self.minimo)
        return self.TOPO + (1 - proporcao) * self.altura_util

    @property
    def pontos(self):
        return [
            {
                "x": round(self._x(r.data), 1),
                "y": round(self._y(r.peso_kg), 1),
                "dica": f"{r.data:%d/%m/%Y}: {formatar_numero(r.peso_kg)} kg",
            }
            for r in self.registros
        ]

    @property
    def linha(self):
        """Texto no formato que o SVG espera: 'x1,y1 x2,y2 x3,y3 ...'."""
        return " ".join(f"{p['x']},{p['y']}" for p in self.pontos)

    @property
    def y_meta(self):
        if self.peso_meta is None:
            return None
        return round(self._y(self.peso_meta), 1)

    @property
    def data_inicio(self):
        return f"{self.registros[0].data:%d/%m/%Y}" if self.registros else ""

    @property
    def data_fim(self):
        return f"{self.registros[-1].data:%d/%m/%Y}" if self.registros else ""
