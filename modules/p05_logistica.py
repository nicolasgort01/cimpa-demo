import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    d = pd.read_csv(DATA/"despachos.csv")
    d["fecha_pedido"]             = pd.to_datetime(d["fecha_pedido"])
    d["fecha_entrega_prometida"]  = pd.to_datetime(d["fecha_entrega_prometida"])
    d["fecha_entrega_real"]       = pd.to_datetime(d["fecha_entrega_real"], errors="coerce")
    return d

def render():
    d = load()
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">C</div>
      <div>
        <div class="cb-title">Logística & Despachos</div>
        <div class="cb-sub">Trazabilidad de entregas · OTD · Rutas y tiempos</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    f1,f2,f3,f4 = st.columns(4)
    with f1:
        sedes = ["Todas"] + sorted(d["sede_origen"].unique().tolist())
        sede_sel = st.selectbox("Sede origen", sedes, key="log_sede")
    with f2:
        ciudades = ["Todas"] + sorted(d["ciudad_destino"].unique().tolist())
        ciu_sel = st.selectbox("Ciudad destino", ciudades, key="log_ciu")
    with f3:
        estados = ["Todos"] + sorted(d["estado"].unique().tolist())
        est_sel = st.selectbox("Estado", estados, key="log_est")
    with f4:
        per = st.selectbox("Período", ["Últimos 30 días","Últimos 60 días","Últimos 90 días","Todo"], key="log_per")

    ref = pd.Timestamp("2026-08-22")
    df = d.copy()
    cut = {"Últimos 30 días":30,"Últimos 60 días":60,"Últimos 90 días":90}.get(per)
    if cut: df = df[df["fecha_pedido"] >= ref - pd.Timedelta(days=cut)]
    if sede_sel != "Todas":  df = df[df["sede_origen"] == sede_sel]
    if ciu_sel  != "Todas":  df = df[df["ciudad_destino"] == ciu_sel]
    if est_sel  != "Todos":  df = df[df["estado"] == est_sel]

    entregados = df[df["estado"] == "Entregado"]
    total_desp   = len(df)
    n_otd        = (entregados["entregado_a_tiempo"] == True).sum()
    n_entregado  = len(entregados)
    pct_otd      = n_otd / n_entregado * 100 if n_entregado else 0
    dias_prom    = entregados["dias_transito"].mean() if len(entregados) else 0
    en_transito  = (df["estado"] == "En tránsito").sum()
    retrasados   = df[(df["estado"] == "En tránsito") & (df["fecha_entrega_prometida"] < ref)].shape[0]
    valor_total  = df["valor_cop"].sum()

    k1,k2,k3,k4,k5,k6 = st.columns(6, gap="small")
    k1.markdown(kpi("Total despachos",   str(total_desp),         "", True, "📦"), unsafe_allow_html=True)
    k2.markdown(kpi("OTD",               pct(pct_otd),            f"{n_otd}/{n_entregado} a tiempo", pct_otd>85, "✅"), unsafe_allow_html=True)
    k3.markdown(kpi("Días tránsito prom",f"{dias_prom:.1f} días",  "", dias_prom<3, "🚚"), unsafe_allow_html=True)
    k4.markdown(kpi("En tránsito",       str(en_transito),         "", True, "🔄"), unsafe_allow_html=True)
    k5.markdown(kpi("Retrasados",        str(retrasados),          "Venc. fecha prometida", retrasados==0, "⚠️"), unsafe_allow_html=True)
    k6.markdown(kpi("Valor despachado",  cop(valor_total,1),       "", True, "💰"), unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3, gap="medium")

    with c1:
        dm = df.copy(); dm["mes"] = dm["fecha_pedido"].dt.to_period("M").astype(str)
        dm_agg = dm.groupby("mes").agg(total=("despacho_id","count"), otd=("entregado_a_tiempo","sum")).reset_index()
        dm_agg["pct_otd"] = (dm_agg["otd"] / dm_agg["total"] * 100).round(1)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=dm_agg["mes"], y=dm_agg["total"], name="Despachos", marker_color=PURPLE, yaxis="y"))
        fig.add_trace(go.Scatter(x=dm_agg["mes"], y=dm_agg["pct_otd"], name="OTD %",
            mode="lines+markers", line=dict(color=TEAL, width=2.5), yaxis="y2"))
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0,105],
            tickfont=dict(color=TEAL, size=11), showgrid=False),
            barmode="group")
        st.plotly_chart(dark(fig, 310, "Despachos mensuales y OTD %"), use_container_width=True)

    with c2:
        estado_cnt = df.groupby("estado").size().reset_index(name="n")
        colores = [estado_color(e) for e in estado_cnt["estado"]]
        fig = go.Figure(go.Pie(labels=estado_cnt["estado"], values=estado_cnt["n"],
            hole=0.5, marker_colors=colores, textinfo="label+percent", textfont_size=11))
        st.plotly_chart(dark(fig, 310, "Estado de despachos"), use_container_width=True)

    with c3:
        ruta = df.groupby(["sede_origen","ciudad_destino"]).size().reset_index(name="n").nlargest(10, "n")
        ruta["ruta"] = ruta["sede_origen"] + " → " + ruta["ciudad_destino"]
        ruta = ruta.sort_values("n")
        fig = go.Figure(go.Bar(x=ruta["n"], y=ruta["ruta"], orientation="h",
            marker_color=PALETTE[:len(ruta)],
            hovertemplate="<b>%{y}</b><br>Despachos: %{x}<extra></extra>"))
        st.plotly_chart(dark(fig, 310, "Top 10 rutas más activas"), use_container_width=True)

    c4,c5 = st.columns(2, gap="medium")
    with c4:
        ent = entregados.copy()
        fig = go.Figure(go.Histogram(x=ent["dias_transito"], nbinsx=15, marker_color=PURPLE, opacity=0.85,
            hovertemplate="Días: %{x}<br>Despachos: %{y}<extra></extra>"))
        fig.add_vline(x=dias_prom, line_dash="dash", line_color=TEAL,
                      annotation_text=f"Prom {dias_prom:.1f}d", annotation_font_color=TEAL)
        st.plotly_chart(dark(fig, 290, "Distribución días de tránsito"), use_container_width=True)

    with c5:
        sede_otd = entregados.groupby("sede_origen").agg(
            total=("despacho_id","count"), a_tiempo=("entregado_a_tiempo","sum")
        ).reset_index()
        sede_otd["otd_pct"] = sede_otd["a_tiempo"] / sede_otd["total"] * 100
        sede_otd = sede_otd.sort_values("otd_pct", ascending=True)
        fig = go.Figure(go.Bar(x=sede_otd["otd_pct"], y=sede_otd["sede_origen"], orientation="h",
            marker_color=[GREEN if v>85 else AMBER if v>70 else RED for v in sede_otd["otd_pct"]],
            hovertemplate="<b>%{y}</b><br>OTD: %{x:.1f}%<extra></extra>"))
        fig.add_vline(x=85, line_dash="dash", line_color=AMBER, opacity=0.6,
                      annotation_text="Meta 85%", annotation_font_color=AMBER)
        st.plotly_chart(dark(fig, 290, "OTD por sede (%)"), use_container_width=True)

    st.markdown(f"<p style='font-weight:700;font-size:14px;color:{TEXT};margin-top:8px'>Detalle de despachos</p>", unsafe_allow_html=True)
    disp = df.sort_values("fecha_pedido", ascending=False).copy()
    disp["valor_cop"] = disp["valor_cop"].apply(cop)
    disp["fecha_pedido"] = disp["fecha_pedido"].dt.strftime("%Y-%m-%d")
    disp["fecha_entrega_prometida"] = disp["fecha_entrega_prometida"].dt.strftime("%Y-%m-%d")
    disp["a_tiempo"] = disp["entregado_a_tiempo"].map({True: "✅ Sí", False: "❌ No", None: "—"})
    st.dataframe(disp[["despacho_id","cliente","sede_origen","ciudad_destino","fecha_pedido",
                        "fecha_entrega_prometida","dias_transito","estado","a_tiempo","valor_cop"]].rename(columns={
        "despacho_id":"ID","cliente":"Cliente","sede_origen":"Origen","ciudad_destino":"Destino",
        "fecha_pedido":"F. Pedido","fecha_entrega_prometida":"F. Prometida","dias_transito":"Días",
        "estado":"Estado","a_tiempo":"A tiempo","valor_cop":"Valor"}),
        hide_index=True, use_container_width=True, height=360)
