import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    c = pd.read_csv(DATA/"cartera.csv")
    c["fecha_factura"]     = pd.to_datetime(c["fecha_factura"])
    c["fecha_vencimiento"] = pd.to_datetime(c["fecha_vencimiento"])
    return c

def render():
    c = load()
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">C</div>
      <div>
        <div class="cb-title">Cartera & Cobranza</div>
        <div class="cb-sub">Cuentas por cobrar · Aging · Alertas de mora</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    f1,f2,f3 = st.columns(3)
    with f1:
        sectores = ["Todos"] + sorted(c["sector"].unique().tolist())
        sec_sel = st.selectbox("Sector", sectores, key="c_sec")
    with f2:
        estados = ["Todos"] + sorted(c["estado"].unique().tolist())
        est_sel = st.selectbox("Estado", estados, key="c_est")
    with f3:
        creds = ["Todos"] + sorted(c["credito_dias"].unique().astype(str).tolist())
        cred_sel = st.selectbox("Días de crédito", creds, key="c_cred")

    df = c.copy()
    if sec_sel != "Todos": df = df[df["sector"] == sec_sel]
    if est_sel != "Todos": df = df[df["estado"] == est_sel]
    if cred_sel != "Todos": df = df[df["credito_dias"] == int(cred_sel)]

    total_car    = df["valor_cop"].sum()
    total_venc   = df[df["dias_mora"] > 0]["valor_cop"].sum()
    pct_venc     = total_venc / total_car * 100 if total_car else 0
    critica      = df[df["dias_mora"] > 90]["valor_cop"].sum()
    dias_car_avg = (df[df["dias_mora"] > 0]["dias_mora"] * df[df["dias_mora"] > 0]["valor_cop"]).sum() / total_venc if total_venc else 0
    n_clientes   = df[df["dias_mora"] > 0]["cliente_id"].nunique()

    k1,k2,k3,k4,k5,k6 = st.columns(6, gap="small")
    k1.markdown(kpi("Cartera total",    cop(total_car,1),  "", True, "📋"), unsafe_allow_html=True)
    k2.markdown(kpi("Cartera vigente",  cop(total_car-total_venc,1), "", True, "✅"), unsafe_allow_html=True)
    k3.markdown(kpi("Cartera vencida",  cop(total_venc,1), pct(pct_venc)+" del total", pct_venc<15, "⚠️"), unsafe_allow_html=True)
    k4.markdown(kpi("Vencida +90 días", cop(critica,1),    "Cartera crítica", critica==0, "🔴"), unsafe_allow_html=True)
    k5.markdown(kpi("Días mora promedio", f"{dias_car_avg:.0f} días", "", dias_car_avg<30, "📅"), unsafe_allow_html=True)
    k6.markdown(kpi("Clientes en mora",  str(n_clientes), "", n_clientes==0, "👤"), unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3, gap="medium")

    with c1:
        buckets = {
            "Vigente":       df[df["dias_mora"]==0]["valor_cop"].sum(),
            "1–30 días":     df[df["dias_mora"].between(1,30)]["valor_cop"].sum(),
            "31–60 días":    df[df["dias_mora"].between(31,60)]["valor_cop"].sum(),
            "61–90 días":    df[df["dias_mora"].between(61,90)]["valor_cop"].sum(),
            "+90 días":      df[df["dias_mora"]>90]["valor_cop"].sum(),
        }
        fig = go.Figure(go.Bar(
            x=list(buckets.keys()), y=list(buckets.values()),
            marker_color=[GREEN, AMBER, "#f97316", RED, "#b91c1c"],
            hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v,1) for v in buckets.values()]))
        st.plotly_chart(dark(fig, 300, "Aging de cartera (COP)"), use_container_width=True)

    with c2:
        cs = df.groupby("sector")["valor_cop"].sum().reset_index().sort_values("valor_cop",ascending=False)
        fig = go.Figure(go.Pie(labels=cs["sector"], values=cs["valor_cop"],
            hole=0.5, marker_colors=PALETTE, textinfo="label+percent", textfont_size=11))
        st.plotly_chart(dark(fig, 300, "Cartera por sector"), use_container_width=True)

    with c3:
        cc = df.groupby("cliente").agg(
            total=("valor_cop","sum"), vencida=("valor_cop", lambda x: x[df.loc[x.index,"dias_mora"]>0].sum())
        ).reset_index().sort_values("vencida",ascending=False).head(8)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Vigente", x=cc["cliente"], y=cc["total"]-cc["vencida"], marker_color=GREEN))
        fig.add_trace(go.Bar(name="Vencida", x=cc["cliente"], y=cc["vencida"], marker_color=RED))
        fig.update_layout(barmode="stack")
        fig.update_xaxes(tickangle=-35)
        st.plotly_chart(dark(fig, 300, "Top clientes: vigente vs vencida"), use_container_width=True)

    # Row 2: mora por ciudad + dias mora distribution
    c4,c5 = st.columns(2, gap="medium")
    with c4:
        cciu = df[df["dias_mora"]>0].groupby("ciudad")["valor_cop"].sum().sort_values(ascending=True).reset_index()
        fig = go.Figure(go.Bar(x=cciu["valor_cop"], y=cciu["ciudad"], orientation="h",
            marker_color=RED, hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v,1) for v in cciu["valor_cop"]]))
        st.plotly_chart(dark(fig, 280, "Cartera vencida por ciudad"), use_container_width=True)

    with c5:
        mora = df[df["dias_mora"]>0]
        fig = go.Figure(go.Histogram(x=mora["dias_mora"], nbinsx=20,
            marker_color=PURPLE, opacity=0.85,
            hovertemplate="Días mora: %{x}<br>Facturas: %{y}<extra></extra>"))
        fig.add_vline(x=30,  line_dash="dash", line_color=AMBER, opacity=0.7)
        fig.add_vline(x=90,  line_dash="dash", line_color=RED,   opacity=0.7)
        st.plotly_chart(dark(fig, 280, "Distribución de días de mora"), use_container_width=True)

    # Detail table
    st.markdown(f"<p style='font-weight:700;font-size:14px;color:{TEXT};margin-top:8px'>Detalle de facturas</p>", unsafe_allow_html=True)
    disp = df.sort_values("dias_mora", ascending=False).copy()
    disp["valor_cop"] = disp["valor_cop"].apply(cop)
    st.dataframe(disp[["factura_id","cliente","sector","ciudad","fecha_factura","fecha_vencimiento","credito_dias","dias_mora","valor_cop","estado"]].rename(columns={
        "factura_id":"Factura","cliente":"Cliente","sector":"Sector","ciudad":"Ciudad",
        "fecha_factura":"Emisión","fecha_vencimiento":"Vencimiento","credito_dias":"Crédito días",
        "dias_mora":"Días mora","valor_cop":"Valor","estado":"Estado"}),
        hide_index=True, use_container_width=True, height=380)
