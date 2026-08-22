import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils.formatters import CSS, HEADER_CSS, BG, SURF, BORDER, TEXT, MUTED, PURPLE, TEAL

st.set_page_config(
    page_title="CIMPA · Panel de Inteligencia de Negocios | Calybrat",
    page_icon="🧴",
    layout="wide",
)

st.markdown(CSS + HEADER_CSS, unsafe_allow_html=True)

PAGES = {
    "🏠  Dashboard General":          "p01_dashboard",
    "📦  Inventario Multi-Bodega":    "p02_inventario",
    "💰  Ventas & Clientes":          "p03_ventas",
    "📋  Cartera & Cobranza":         "p04_cartera",
    "🚚  Logística & Despachos":      "p05_logistica",
    "🌐  Proveedores & Compras":      "p06_proveedores",
    "👥  Talento Humano":             "p07_talento",
    "🏢  Consolidado del Grupo":      "p08_grupo",
    "📄  Reportes Automáticos":       "p10_reportes",
    "🤖  Agente IA CIMPA":            "p09_agente",
}

with st.sidebar:
    st.markdown(f"""
    <div style="padding:18px 4px 20px">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
        <div style="width:38px;height:38px;border-radius:10px;
          background:linear-gradient(135deg,{PURPLE},{TEAL});
          display:flex;align-items:center;justify-content:center;
          font-size:18px;font-weight:900;color:white;
          box-shadow:0 0 14px {PURPLE}55">C</div>
        <div>
          <div style="font-size:16px;font-weight:800;color:{TEXT}">CIMPA</div>
          <div style="font-size:11px;color:{MUTED}">Panel de Negocios</div>
        </div>
      </div>
      <div style="height:1px;background:linear-gradient(90deg,{PURPLE},{TEAL},transparent);margin:14px 0 6px"></div>
    </div>
    """, unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = list(PAGES.keys())[0]

    for label in PAGES:
        active = st.session_state.page == label
        btn_style = (f"background:linear-gradient(135deg,{PURPLE}33,{TEAL}22);"
                     f"border:1px solid {PURPLE}44;" if active else
                     f"background:transparent;border:1px solid transparent;")
        if st.button(label, key=f"nav_{label}", use_container_width=True):
            st.session_state.page = label

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="padding:12px 16px 8px;text-align:center;border-top:1px solid {BORDER};margin-top:8px">
      <div style="font-size:10.5px;color:{MUTED};margin-bottom:2px">Construido por</div>
      <div style="font-size:13px;font-weight:700;
        background:linear-gradient(135deg,{PURPLE},{TEAL});
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text">Calybrat</div>
      <div style="font-size:10px;color:{MUTED}55;margin-top:2px">© 2026 · Demo</div>
    </div>
    """, unsafe_allow_html=True)

# ── Load active module ────────────────────────────────────────────────────────
module_name = PAGES[st.session_state.page]
try:
    mod = __import__(f"modules.{module_name}", fromlist=[module_name])
    mod.render()
except Exception as e:
    st.error(f"Error cargando módulo: {e}")
    import traceback; st.code(traceback.format_exc())
