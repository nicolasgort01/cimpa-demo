import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    v = pd.read_csv(DATA/"ventas.csv")
    v["fecha"] = pd.to_datetime(v["fecha"])
    return v

def render():
    v = load()
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">C</div>
      <div>
        <div class="cb-title">Ventas & Clientes</div>
        <div class="cb-sub">Análisis comercial por sede, sector, cliente y producto</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    # Filters
    f1,f2,f3,f4 = st.columns(4)
    with f1:
        per = st.selectbox("Período", ["Últimos 30 días","Últimos 60 días","Últimos 90 días","2026 (YTD)","2025 completo"], key="v_per")
    with f2:
        sedes = ["Todas"] + sorted(v["sede_id"].unique().tolist())
        sede_sel = st.selectbox("Sede", sedes, key="v_sede")
    with f3:
        sectores = ["Todos"] + sorted(v["sector_cliente"].unique().tolist())
        sec_sel = st.selectbox("Sector cliente", sectores, key="v_sec")
    with f4:
        cats = ["Todas"] + sorted(v["categoria"].unique().tolist())
        cat_sel = st.selectbox("Categoría", cats, key="v_cat")

    ref = pd.Timestamp("2026-08-22")
    cutoff = {"Últimos 30 días":30,"Últimos 60 días":60,"Últimos 90 días":90}.get(per)
    if cutoff:
        vf = v[v["fecha"] >= ref - pd.Timedelta(days=cutoff)]
        vp = v[(v["fecha"] >= ref - pd.Timedelta(days=cutoff*2)) & (v["fecha"] < ref - pd.Timedelta(days=cutoff))]
    elif per == "2026 (YTD)":
        vf = v[v["fecha"].dt.year == 2026]; vp = v[v["fecha"].dt.year == 2025]
    else:
        vf = v[v["fecha"].dt.year == 2025]; vp = v[v["fecha"].dt.year == 2024]

    if sede_sel != "Todas": vf = vf[vf["sede_id"] == sede_sel]; vp = vp[vp["sede_id"] == sede_sel]
    if sec_sel  != "Todos": vf = vf[vf["sector_cliente"] == sec_sel]; vp = vp[vp["sector_cliente"] == sec_sel]
    if cat_sel  != "Todas": vf = vf[vf["categoria"] == cat_sel]; vp = vp[vp["categoria"] == cat_sel]

    vt = vf["total_cop"].sum(); vt_ant = vp["total_cop"].sum()
    dv = (vt - vt_ant) / vt_ant * 100 if vt_ant else 0
    n_ord = len(vf); ticket = vt / n_ord if n_ord else 0
    margen = vf["margen_pct"].mean() * 100 if len(vf) else 0
    n_cli = vf["cliente_id"].nunique()

    k1,k2,k3,k4,k5 = st.columns(5, gap="small")
    k1.markdown(kpi("Ventas totales", cop(vt,1), f"{'▲' if dv>=0 else '▼'} {abs(dv):.1f}% vs anterior", dv>=0, "💰"), unsafe_allow_html=True)
    k2.markdown(kpi("N° órdenes", f"{n_ord:,}", "", True, "🧾"), unsafe_allow_html=True)
    k3.markdown(kpi("Ticket promedio", cop(ticket), "", True, "📌"), unsafe_allow_html=True)
    k4.markdown(kpi("Margen bruto", pct(margen), "", margen>30, "📊"), unsafe_allow_html=True)
    k5.markdown(kpi("Clientes activos", str(n_cli), "", True, "🤝"), unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # Row 1: Trend + by sector
    c1,c2 = st.columns([1.6,1], gap="medium")
    with c1:
        vm = vf.copy(); vm["semana"] = vm["fecha"].dt.to_period("W").astype(str)
        vs = vm.groupby("semana")["total_cop"].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=vs["semana"], y=vs["total_cop"], marker_color=PURPLE, name="Ventas",
            hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v,1) for v in vs["total_cop"]]))
        fig.add_trace(go.Scatter(x=vs["semana"], y=vs["total_cop"].rolling(4,min_periods=1).mean(),
            mode="lines", line=dict(color=TEAL,width=2.5), name="Media 4 sem."))
        st.plotly_chart(dark(fig, 320, "Ventas por semana (COP)"), use_container_width=True)

    with c2:
        vs2 = vf.groupby("sector_cliente")["total_cop"].sum().reset_index().sort_values("total_cop",ascending=False)
        fig = go.Figure(go.Pie(labels=vs2["sector_cliente"], values=vs2["total_cop"],
            hole=0.52, marker_colors=PALETTE, textinfo="label+percent", textfont_size=11,
            hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v,1) for v in vs2["total_cop"]]))
        st.plotly_chart(dark(fig, 320, "Participación por sector"), use_container_width=True)

    # Row 2: by sede + top products
    c3,c4 = st.columns(2, gap="medium")
    with c3:
        sede_names = {"BOG-AME":"Bogotá Américas","BOG-QUI":"Bogotá Químicos",
                      "ITA":"Itagüí","VIL":"Villavicencio","TUN":"Tunja","MOS":"CEDI Mosquera","SIB":"CEDI Siberia"}
        vs3 = vf.groupby("sede_id")["total_cop"].sum().reset_index()
        vs3["sede_nombre"] = vs3["sede_id"].map(sede_names)
        vs3 = vs3.sort_values("total_cop")
        fig = go.Figure(go.Bar(x=vs3["total_cop"], y=vs3["sede_nombre"], orientation="h",
            marker_color=PALETTE[:len(vs3)],
            hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v,1) for v in vs3["total_cop"]]))
        st.plotly_chart(dark(fig, 300, "Ventas por sede"), use_container_width=True)

    with c4:
        tp = vf.groupby("producto")["total_cop"].sum().nlargest(10).reset_index().sort_values("total_cop")
        fig = go.Figure(go.Bar(x=tp["total_cop"], y=tp["producto"], orientation="h",
            marker_color=TEAL,
            hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v,1) for v in tp["total_cop"]]))
        st.plotly_chart(dark(fig, 300, "Top 10 productos más vendidos"), use_container_width=True)

    # Row 3: Top clients + margen por categoria
    c5,c6 = st.columns(2, gap="medium")
    with c5:
        tc = vf.groupby("cliente")["total_cop"].sum().nlargest(10).reset_index().sort_values("total_cop")
        fig = go.Figure(go.Bar(x=tc["total_cop"], y=tc["cliente"], orientation="h",
            marker_color=PURPLE,
            hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v,1) for v in tc["total_cop"]]))
        st.plotly_chart(dark(fig, 300, "Top 10 clientes por ingresos"), use_container_width=True)

    with c6:
        mc = vf.groupby("categoria")["margen_pct"].mean().reset_index().sort_values("margen_pct",ascending=False)
        mc["margen_pct"] *= 100
        fig = go.Figure(go.Bar(x=mc["categoria"], y=mc["margen_pct"],
            marker_color=[GREEN if m>35 else AMBER if m>25 else RED for m in mc["margen_pct"]],
            hovertemplate="<b>%{x}</b><br>Margen: %{y:.1f}%<extra></extra>"))
        fig.add_hline(y=30, line_dash="dash", line_color=AMBER, opacity=0.6,
                      annotation_text="Meta 30%", annotation_font_color=AMBER)
        st.plotly_chart(dark(fig, 300, "Margen bruto promedio por categoría (%)"), use_container_width=True)

    # Detail table
    st.markdown(f"<p style='font-weight:700;font-size:14px;color:{TEXT};margin-top:8px'>Detalle de ventas</p>", unsafe_allow_html=True)
    disp = vf.groupby(["cliente","sector_cliente","categoria","producto","sede_id"]).agg(
        ordenes=("total_cop","count"),
        total_cop=("total_cop","sum"),
        margen_pct=("margen_pct","mean")
    ).reset_index().sort_values("total_cop",ascending=False).head(200)
    disp["total_cop"] = disp["total_cop"].apply(cop)
    disp["margen_pct"] = (disp["margen_pct"]*100).round(1).astype(str) + "%"
    st.dataframe(disp.rename(columns={
        "cliente":"Cliente","sector_cliente":"Sector","categoria":"Categoría",
        "producto":"Producto","sede_id":"Sede","ordenes":"Órdenes",
        "total_cop":"Ventas","margen_pct":"Margen"}),
        hide_index=True, use_container_width=True, height=340)
