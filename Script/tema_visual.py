import matplotlib as mpl
import matplotlib.pyplot as plt
from IPython.display import display, HTML
import pandas as pd

COR_ACENTO = "#7EF3C4"
COR_AVISO  = "#FFD166"
COR_FUNDO  = "#111111"
COR_TEXTO  = "#F7FFF9"
COR_BORDA  = "#7EF3C4"
COR_MUTED  = "#A7B8B2"


def aplicar_estilo_notebook():
    """Injeta CSS para outputs e markdown renderizado no notebook."""
    display(HTML(
        """
<style>
:root {
  --volix-primary: #1B9AAA;
  --volix-accent: #06D6A0;
  --volix-accent-light: #7EF3C4;
  --volix-border: #7EF3C4;
  --volix-ink: #F7FFF9;
  --volix-muted: #A7B8B2;
  --volix-panel: #171717;
  --volix-panel-soft: #1F1F1F;
  --volix-panel-strong: #111111;
  --volix-warning: #FFD166;
}

.jp-Notebook,
.jp-Cell,
body {
  background: var(--volix-panel-strong) !important;
  color: var(--volix-ink) !important;
}

.jp-RenderedHTMLCommon,
.jp-RenderedHTMLCommon p,
.jp-RenderedHTMLCommon li,
.jp-RenderedHTMLCommon td {
  color: var(--volix-ink) !important;
  font-size: 15px;
  line-height: 1.58;
}

.jp-RenderedHTMLCommon h1,
.jp-RenderedHTMLCommon h2,
.jp-RenderedHTMLCommon h3 {
  color: var(--volix-ink) !important;
  font-weight: 850 !important;
  letter-spacing: 0 !important;
}

.jp-RenderedHTMLCommon code {
  background: #1B1B1B !important;
  color: var(--volix-accent-light) !important;
  border-radius: 4px;
  padding: 2px 6px;
}

.jp-InputArea-editor,
.cm-editor,
.cell.code_cell .input_area {
  background: #101010 !important;
  color: var(--volix-ink) !important;
  border-left: 8px solid var(--volix-border) !important;
}

.jp-CodeCell .jp-Cell-inputWrapper {
  border: 4px solid rgba(221,247,236,.75) !important;
  border-radius: 8px !important;
  overflow: hidden !important;
}

.jp-OutputArea-output pre,
.output_subarea pre {
  background: #101010 !important;
  color: var(--volix-ink) !important;
  border: 3px solid var(--volix-border) !important;
  border-radius: 8px !important;
  padding: 14px 16px !important;
  font-size: 13px !important;
  white-space: pre-wrap !important;
}

.dataframe {
  background: var(--volix-panel) !important;
  color: var(--volix-ink) !important;
  border-radius: 8px !important;
  overflow: hidden !important;
  border: 3px solid var(--volix-border) !important;
}

.dataframe th {
  background: rgba(6,214,160,.20) !important;
  color: #FFFFFF !important;
  border-bottom: 4px solid var(--volix-border) !important;
}

.dataframe td {
  color: var(--volix-ink) !important;
  border-color: rgba(221,247,236,.12) !important;
}
</style>
        """
    ))


def configurar_tema():
    aplicar_estilo_notebook()
    mpl.rcParams.update({
        "figure.facecolor":  COR_FUNDO,
        "axes.facecolor":    COR_FUNDO,
        "axes.edgecolor":    "#333333",
        "axes.labelcolor":   COR_TEXTO,
        "text.color":        COR_TEXTO,
        "xtick.color":       COR_MUTED,
        "ytick.color":       COR_MUTED,
        "grid.color":        "#222222",
        "grid.linestyle":    "--",
        "grid.linewidth":    0.6,
        "font.family":       "sans-serif",
        "figure.dpi":        110,
    })
    display(HTML(
        '<div style="border:2px solid #7EF3C4;background:#111111;border-radius:8px;'
        'padding:10px 18px;margin:6px 0;display:inline-block;">'
        '<span style="color:#7EF3C4;font-size:11px;font-weight:900;text-transform:uppercase;'
        'letter-spacing:.18em;">✓  Tema Volix aplicado</span>'
        '</div>'
    ))


def fmt_num(val):
    if isinstance(val, float):
        if abs(val) >= 1_000_000:
            return f"{val / 1_000_000:.1f}M"
        if abs(val) >= 1_000:
            return f"{val / 1_000:.1f}k"
        return f"{val:,.2f}"
    if isinstance(val, int):
        if abs(val) >= 1_000_000:
            return f"{val / 1_000_000:.1f}M"
        if abs(val) >= 1_000:
            return f"{val / 1_000:.1f}k"
        return f"{val:,}"
    return str(val)


def painel_kpis_terminal(kpis, titulo=""):
    cards = ""
    for label, valor, cor in kpis:
        cards += (
            f'<div style="flex:1;min-width:130px;border:2px solid {cor};background:#171717;'
            f'border-radius:8px;padding:14px 16px;box-sizing:border-box;">'
            f'<div style="color:#A7B8B2;font-size:11px;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.12em;margin-bottom:6px;">{label}</div>'
            f'<div style="color:{cor};font-size:22px;font-weight:900;font-family:monospace;">{valor}</div>'
            f'</div>'
        )
    header = (
        f'<div style="color:#7EF3C4;font-size:11px;font-weight:900;text-transform:uppercase;'
        f'letter-spacing:.18em;margin-bottom:12px;">{titulo}</div>'
    ) if titulo else ""
    display(HTML(
        '<div style="border:2px solid #7EF3C4;background:#111111;border-radius:8px;'
        'padding:18px 22px;margin:8px 0;">'
        + header
        + f'<div style="display:flex;gap:12px;flex-wrap:wrap;">{cards}</div>'
        + '</div>'
    ))


def tabela_terminal(df, titulo=""):
    headers = "".join(
        f'<th style="background:rgba(6,214,160,.20);color:#FFFFFF;border-bottom:4px solid #7EF3C4;'
        f'padding:8px 12px;text-align:left;white-space:nowrap;">{c}</th>'
        for c in df.columns
    )
    rows = ""
    for _, row in df.iterrows():
        cells = "".join(
            f'<td style="color:#F7FFF9;border-bottom:1px solid rgba(221,247,236,.08);'
            f'padding:7px 12px;white-space:nowrap;">{v}</td>'
            for v in row
        )
        rows += f'<tr>{cells}</tr>'
    header_html = (
        f'<div style="color:#7EF3C4;font-size:11px;font-weight:900;text-transform:uppercase;'
        f'letter-spacing:.18em;margin-bottom:10px;">{titulo}</div>'
    ) if titulo else ""
    display(HTML(
        '<div style="border:2px solid #7EF3C4;background:#111111;border-radius:8px;'
        'padding:18px 22px;margin:8px 0;overflow-x:auto;">'
        + header_html
        + '<table style="border-collapse:collapse;width:100%;">'
        + f'<thead><tr>{headers}</tr></thead>'
        + f'<tbody>{rows}</tbody>'
        + '</table></div>'
    ))


def cabecalho_secao(nome, badge=""):
    b = (
        f'<span style="background:#7EF3C4;color:#111111;font-weight:900;font-size:11px;'
        f'padding:3px 10px;border-radius:4px;margin-right:10px;">{badge}</span>'
    ) if badge else ""
    display(HTML(
        f'<div style="color:#7EF3C4;font-weight:900;font-size:13px;letter-spacing:.12em;'
        f'text-transform:uppercase;margin:18px 0 8px 0;">{b}{nome}</div>'
    ))


def nota_aviso(mensagem, titulo="Aviso"):
    display(HTML(
        f'<div style="border:2px solid {COR_AVISO};background:rgba(255,209,102,.08);'
        f'border-radius:8px;padding:12px 16px;margin:8px 0;">'
        f'<div style="color:{COR_AVISO};font-size:11px;font-weight:900;text-transform:uppercase;'
        f'letter-spacing:.18em;margin-bottom:8px;">{titulo}</div>'
        f'<div style="color:{COR_TEXTO};font-size:13px;line-height:1.6;">{mensagem}</div>'
        f'</div>'
    ))


def aplicar_estilo_grafico(ax):
    ax.set_facecolor(COR_FUNDO)
    ax.set_axisbelow(True)
    ax.tick_params(colors=COR_MUTED)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#333333")
    ax.spines["bottom"].set_color("#333333")
    ax.grid(True, color="#2A2A2A", linestyle="--", linewidth=0.6)
    xlabel = ax.get_xlabel()
    ylabel = ax.get_ylabel()
    if xlabel:
        ax.set_xlabel(xlabel, color=COR_MUTED)
    if ylabel:
        ax.set_ylabel(ylabel, color=COR_MUTED)
