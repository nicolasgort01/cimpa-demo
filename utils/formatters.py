import plotly.graph_objects as go

BG     = "#0a0a0f"
SURF   = "#111118"
SURF2  = "#18181f"
BORDER = "rgba(255,255,255,0.08)"
TEXT   = "#eeeef2"
MUTED  = "#7e7e96"
DIM    = "#3a3a4a"
PURPLE = "#6c63ff"
TEAL   = "#3ecfcf"
GREEN  = "#22c55e"
AMBER  = "#f59e0b"
RED    = "#ef4444"
SKY    = "#38bdf8"
GRAD   = [PURPLE, TEAL]

PALETTE = [PURPLE, TEAL, "#f59e0b", "#22c55e", "#ef4444", "#38bdf8", "#a78bfa", "#34d399"]


def cop(v, decimals=0) -> str:
    """Format COP value: 1.23B, 456M, 12.3K"""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    if abs(v) >= 1_000_000_000:
        return f"${v/1_000_000_000:,.{decimals}f}B"
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:,.{decimals}f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:,.{decimals}f}K"
    return f"${v:,.{decimals}f}"


def pct(v, decimals=1) -> str:
    try:
        return f"{float(v):.{decimals}f}%"
    except (TypeError, ValueError):
        return "—"


def dark(fig: go.Figure, height: int = 340, title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=TEXT), x=0, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, system-ui, sans-serif", color=MUTED, size=12),
        height=height,
        margin=dict(l=6, r=6, t=44 if title else 16, b=6),
        legend=dict(orientation="h", y=1.12, x=0, font=dict(color=MUTED, size=11)),
        hovermode="x unified",
        colorway=PALETTE,
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False, tickfont=dict(color=MUTED))
    return fig


def kpi(label: str, value: str, delta: str = "", delta_good: bool = True, icon: str = "") -> str:
    color = GREEN if delta_good else RED
    delta_html = f'<p style="font-size:12px;color:{color};margin:4px 0 0">{delta}</p>' if delta else ""
    icon_html  = f'<div style="font-size:22px;margin-bottom:8px">{icon}</div>' if icon else ""
    return f"""
    <div style="background:{SURF};border:1px solid {BORDER};border-radius:12px;padding:18px 16px;height:100%">
      {icon_html}
      <p style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:{MUTED};margin:0">{label}</p>
      <p style="font-size:26px;font-weight:800;color:{TEXT};margin:6px 0 0;letter-spacing:-.5px;line-height:1">{value}</p>
      {delta_html}
    </div>"""


def estado_color(estado: str) -> str:
    m = {"Crítico": RED, "Bajo": AMBER, "Normal": GREEN, "Alto": SKY,
         "Entregado": GREEN, "En tránsito": SKY, "Generado": MUTED,
         "Pendiente despacho": AMBER, "En aduana": AMBER,
         "Vigente": GREEN, "Vencida 1-30": AMBER,
         "Vencida 31-60": "#f97316", "Vencida 61-90": RED, "Vencida +90": "#b91c1c"}
    return m.get(estado, MUTED)


CSS = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  html, body, [class*="css"] {{ font-family:'Inter',-apple-system,system-ui,sans-serif; }}
  .stApp {{ background:{BG}; color:{TEXT}; }}
  section[data-testid="stSidebar"] {{ background:#08080e; border-right:1px solid {BORDER}; }}
  .block-container {{ padding-top:1.8rem !important; }}
  div[data-testid="stMetricValue"] {{ color:{TEXT}; }}
  .stDataFrame {{ border-radius:10px; overflow:hidden; }}
  thead tr th {{ background:{SURF2} !important; color:{MUTED} !important; font-size:12px !important; text-transform:uppercase; letter-spacing:.06em; }}
  tbody tr:hover td {{ background:rgba(108,99,255,.06) !important; }}
  div[data-baseweb="select"] > div {{ background:{SURF} !important; border-color:{BORDER} !important; }}
  div[data-baseweb="select"] span {{ color:{TEXT} !important; }}
  .stMultiSelect span[data-baseweb="tag"] {{ background:{PURPLE}33 !important; }}
  button[kind="primary"] {{ background:linear-gradient(135deg,{PURPLE},{TEAL}) !important; border:none !important; }}
  .stTabs [data-baseweb="tab"] {{ background:{SURF}; border-radius:8px 8px 0 0; }}
  .stTabs [aria-selected="true"] {{ background:{PURPLE}22 !important; }}
  div[data-testid="stExpander"] {{ border-color:{BORDER} !important; background:{SURF} !important; }}
</style>
"""

HEADER_CSS = f"""
<style>
  .cb-header {{ display:flex;align-items:center;gap:16px;padding:2px 0 }}
  .cb-logo {{ width:44px;height:44px;border-radius:50%;
    background-image:url('data:image/png;base64,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');
    background-size:cover;background-position:center;
    display:flex;align-items:center;justify-content:center;
    font-size:0;color:transparent;
    box-shadow:0 0 18px {PURPLE}44 }}
  .cb-title {{ font-size:24px;font-weight:800;color:{TEXT};letter-spacing:-.4px }}
  .cb-sub {{ font-size:13px;color:{MUTED};margin-top:2px }}
  .cb-rule {{ height:1px;background:linear-gradient(90deg,{PURPLE},{TEAL},transparent);margin:14px 0 20px }}
  .cb-badge {{ display:inline-block;background:{PURPLE}22;color:{PURPLE};
    border:1px solid {PURPLE}44;border-radius:999px;
    padding:2px 12px;font-size:11px;font-weight:700;letter-spacing:.06em }}
  .cb-teal  {{ display:inline-block;background:{TEAL}22;color:{TEAL};
    border:1px solid {TEAL}44;border-radius:999px;
    padding:2px 12px;font-size:11px;font-weight:700;letter-spacing:.06em }}
</style>
"""
