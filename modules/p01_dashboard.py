import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    v  = pd.read_csv(DATA/"ventas.csv")
    v["fecha"] = pd.to_datetime(v["fecha"])
    c  = pd.read_csv(DATA/"cartera.csv")
    c["fecha_vencimiento"] = pd.to_datetime(c["fecha_vencimiento"])
    d  = pd.read_csv(DATA/"despachos.csv")
    d["fecha_pedido"]            = pd.to_datetime(d["fecha_pedido"])
    d["fecha_entrega_prometida"] = pd.to_datetime(d["fecha_entrega_prometida"])
    i  = pd.read_csv(DATA/"inventario.csv")
    return v, c, d, i

def render():
    v, c, d, inv = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">C</div>
      <div>
        <div class="cb-title">CIMPA · Dashboard General</div>
        <div class="cb-sub">30 años · +2.000 insumos · 6 sucursales · Resumen ejecutivo · 22 de agosto 2026</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    # ── Filters ────────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
    with col_f1:
        periodo = st.selectbox("Período", ["Últimos 30 días","Últimos 60 días","Últimos 90 días","2026 (YTD)","2025 completo"], key="db_per")
    with col_f2:
        sedes_all = ["Todas"] + sorted(v["sede_id"].unique().tolist())
        sede_sel  = st.selectbox("Sede", sedes_all, key="db_sede")
    with col_f3:
        cats_all = ["Todas"] + sorted(v["categoria"].unique().tolist())
        cat_sel  = st.selectbox("Categoría", cats_all, key="db_cat")

    # Apply filters
    cutoff = {"Últimos 30 días": 30, "Últimos 60 días": 60, "Últimos 90 días": 90}.get(periodo)
    ref_date = pd.Timestamp("2026-08-22")
    if cutoff:
        vf = v[v["fecha"] >= ref_date - pd.Timedelta(days=cutoff)]
        vp = v[(v["fecha"] >= ref_date - pd.Timedelta(days=cutoff*2)) &
               (v["fecha"] < ref_date - pd.Timedelta(days=cutoff))]
    elif periodo == "2026 (YTD)":
        vf = v[v["fecha"].dt.year == 2026]
        vp = v[v["fecha"].dt.year == 2025]
    else:
        vf = v[v["fecha"].dt.year == 2025]
        vp = v[v["fecha"].dt.year == 2024]

    if sede_sel != "Todas":
        vf = vf[vf["sede_id"] == sede_sel]
        vp = vp[vp["sede_id"] == sede_sel]
    if cat_sel != "Todas":
        vf = vf[vf["categoria"] == cat_sel]
        vp = vp[vp["categoria"] == cat_sel]

    ventas_act = vf["total_cop"].sum()
    ventas_ant = vp["total_cop"].sum()
    delta_v    = (ventas_act - ventas_ant) / ventas_ant * 100 if ventas_ant else 0

    cartera_total   = c["valor_cop"].sum()
    cartera_vencida = c[c["dias_mora"] > 0]["valor_cop"].sum()
    pct_vencida     = cartera_vencida / cartera_total * 100 if cartera_total else 0

    despachos_mes  = d[d["fecha_pedido"] >= ref_date - pd.Timedelta(days=30)]
    ent_a_tiempo   = despachos_mes[despachos_mes["entregado_a_tiempo"] == True].shape[0]
    ent_total      = despachos_mes[despachos_mes["estado"] == "Entregado"].shape[0]
    pct_otd        = ent_a_tiempo / ent_total * 100 if ent_total else 0

    inv_critico = inv[inv["estado"] == "Crítico"].shape[0]
    inv_bajo    = inv[inv["estado"] == "Bajo"].shape[0]
    valor_inv   = inv.groupby("producto_id")["valor_inventario"].sum().sum()

    clientes_act = vf["cliente_id"].nunique()
    margen_avg   = vf["margen_pct"].mean() * 100 if len(vf) else 0

    # ── KPIs ──────────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    k1.markdown(kpi("Ventas período", cop(ventas_act, 1),
        f"{'▲' if delta_v>=0 else '▼'} {abs(delta_v):.1f}% vs anterior", delta_v >= 0, "💰"), unsafe_allow_html=True)
    k2.markdown(kpi("Clientes activos", str(clientes_act), "", True, "🤝"), unsafe_allow_html=True)
    k3.markdown(kpi("Margen bruto", pct(margen_avg), "", margen_avg > 30, "📊"), unsafe_allow_html=True)
    k4.markdown(kpi("Cartera vencida", cop(cartera_vencida, 1),
        f"{pct_vencida:.1f}% del total", pct_vencida < 15, "📋"), unsafe_allow_html=True)
    k5.markdown(kpi("OTD despachos", pct(pct_otd), f"{ent_a_tiempo}/{ent_total} entregas", pct_otd > 85, "🚚"), unsafe_allow_html=True)
    k6.markdown(kpi("SKUs críticos/bajos", f"{inv_critico + inv_bajo}",
        f"{inv_critico} críticos · {inv_bajo} bajos", inv_critico == 0, "📦"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ── Row 1: Ventas mensual + por sede ─────────────────────────────────────
    c1, c2 = st.columns([1.6, 1], gap="medium")

    with c1:
        vm = v[v["fecha"].dt.year.isin([2025, 2026])].copy()
        vm["mes"] = vm["fecha"].dt.to_period("M").astype(str)
        vm_agg = vm.groupby("mes")["total_cop"].sum().reset_index().sort_values("mes")
        fig = go.Figure()
        colors = [PURPLE if m.startswith("2025") else TEAL for m in vm_agg["mes"]]
        fig.add_trace(go.Bar(
            x=vm_agg["mes"], y=vm_agg["total_cop"],
            marker_color=colors, name="Ventas",
            hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v, 1) for v in vm_agg["total_cop"]],
        ))
        fig.add_trace(go.Scatter(
            x=vm_agg["mes"], y=vm_agg["total_cop"].rolling(3, min_periods=1).mean(),
            mode="lines", line=dict(color=AMBER, width=2, dash="dot"),
            name="Media 3 meses",
        ))
        st.plotly_chart(dark(fig, 320, "Ventas mensuales · 2025–2026 (COP)"), use_container_width=True)

    with c2:
        vs = vf.groupby("sede_id")["total_cop"].sum().reset_index().sort_values("total_cop", ascending=True)
        sede_names = {"BOG-AME":"Bogotá Américas","BOG-QUI":"Bogotá Químicos",
                      "ITA":"Itagüí","VIL":"Villavicencio","TUN":"Tunja","MOS":"CEDI Mosquera","SIB":"CEDI Siberia"}
        vs["sede_nombre"] = vs["sede_id"].map(sede_names)
        fig = go.Figure(go.Bar(
            x=vs["total_cop"], y=vs["sede_nombre"], orientation="h",
            marker=dict(color=PALETTE[:len(vs)]),
            hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v, 1) for v in vs["total_cop"]],
        ))
        st.plotly_chart(dark(fig, 320, "Ventas por sede"), use_container_width=True)

    # ── Row 2: Categorías + Top clientes + Cartera aging ─────────────────────
    c3, c4, c5 = st.columns(3, gap="medium")

    with c3:
        vc = vf.groupby("categoria")["total_cop"].sum().reset_index().sort_values("total_cop", ascending=False)
        fig = go.Figure(go.Pie(
            labels=vc["categoria"], values=vc["total_cop"],
            hole=0.52, marker_colors=PALETTE,
            textinfo="label+percent", textfont_size=11,
            hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v, 1) for v in vc["total_cop"]],
        ))
        st.plotly_chart(dark(fig, 300, "Ventas por categoría"), use_container_width=True)

    with c4:
        tc = vf.groupby("cliente")["total_cop"].sum().nlargest(8).reset_index().sort_values("total_cop")
        fig = go.Figure(go.Bar(
            x=tc["total_cop"], y=tc["cliente"], orientation="h",
            marker_color=TEAL,
            hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v, 1) for v in tc["total_cop"]],
        ))
        st.plotly_chart(dark(fig, 300, "Top 8 clientes"), use_container_width=True)

    with c5:
        buckets = {"Vigente": c[c["dias_mora"]==0]["valor_cop"].sum(),
                   "1–30 días": c[c["dias_mora"].between(1,30)]["valor_cop"].sum(),
                   "31–60 días": c[c["dias_mora"].between(31,60)]["valor_cop"].sum(),
                   "61–90 días": c[c["dias_mora"].between(61,90)]["valor_cop"].sum(),
                   "+90 días": c[c["dias_mora"]>90]["valor_cop"].sum()}
        fig = go.Figure(go.Bar(
            x=list(buckets.keys()), y=list(buckets.values()),
            marker_color=[GREEN, AMBER, "#f97316", RED, "#b91c1c"],
            hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v, 1) for v in buckets.values()],
        ))
        st.plotly_chart(dark(fig, 300, "Aging de cartera"), use_container_width=True)

    # ── Alertas ───────────────────────────────────────────────────────────────
    st.markdown(f"<div style='height:8px'></div>", unsafe_allow_html=True)
    with st.expander("⚠️  Alertas del sistema", expanded=True):
        a1, a2, a3 = st.columns(3)
        criticos = inv[inv["estado"] == "Crítico"][["sede_nombre","producto","stock_actual","stock_minimo"]].head(5)
        mora_alta = c[c["dias_mora"] > 60][["cliente","dias_mora","valor_cop"]].sort_values("dias_mora", ascending=False).head(5)
        desp_retrasados = d[(d["estado"]=="En tránsito") &
                             (d["fecha_pedido"] < ref_date - pd.Timedelta(days=5))][["cliente","fecha_pedido","ciudad_destino"]].head(5)
        with a1:
            st.markdown(f"<span style='color:{RED};font-weight:700'>📦 Stock crítico ({len(criticos)} SKUs)</span>", unsafe_allow_html=True)
            st.dataframe(criticos, hide_index=True, use_container_width=True)
        with a2:
            st.markdown(f"<span style='color:{RED};font-weight:700'>📋 Cartera vencida +60d ({len(mora_alta)} facturas)</span>", unsafe_allow_html=True)
            mora_alta_disp = mora_alta.copy()
            mora_alta_disp["valor_cop"] = mora_alta_disp["valor_cop"].apply(cop)
            st.dataframe(mora_alta_disp, hide_index=True, use_container_width=True)
        with a3:
            st.markdown(f"<span style='color:{AMBER};font-weight:700'>🚚 Despachos demorados ({len(desp_retrasados)})</span>", unsafe_allow_html=True)
            st.dataframe(desp_retrasados, hide_index=True, use_container_width=True)
