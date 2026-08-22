import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    g = pd.read_csv(DATA/"grupo_mensual.csv")
    g["periodo"] = pd.to_datetime(g["periodo"])
    return g

def render():
    g = load()
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">C</div>
      <div>
        <div class="cb-title">Consolidado del Grupo</div>
        <div class="cb-sub">CIMPA · Confía Control · Vasanico — Vista consolidada multi-empresa</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    f1,f2 = st.columns(2)
    with f1:
        empresas_all = ["Grupo completo"] + sorted(g["empresa"].unique().tolist())
        emp_sel = st.selectbox("Empresa", empresas_all, key="gr_emp")
    with f2:
        anos = ["2025-2026"] + [str(a) for a in sorted(g["periodo"].dt.year.unique())]
        ano_sel = st.selectbox("Año", anos, key="gr_ano")

    df = g.copy()
    if emp_sel != "Grupo completo": df = df[df["empresa"] == emp_sel]
    if ano_sel != "2025-2026": df = df[df["periodo"].dt.year == int(ano_sel)]

    agg = df.groupby("periodo").agg(
        ventas=("ventas_cop","sum"), margen=("margen_bruto_cop","sum"),
        ebitda=("ebitda_cop","sum"), cartera=("cartera_cop","sum"),
        empleados=("n_empleados","sum")
    ).reset_index().sort_values("periodo")

    # Latest 12-month sums
    total_ventas  = agg["ventas"].sum()
    total_margen  = agg["margen"].sum()
    pct_margen    = total_margen / total_ventas * 100 if total_ventas else 0
    total_ebitda  = agg["ebitda"].sum()
    pct_ebitda    = total_ebitda / total_ventas * 100 if total_ventas else 0
    cartera_act   = df[df["periodo"] == df["periodo"].max()].groupby("empresa")["cartera_cop"].sum().sum()
    n_emp_act     = df[df["periodo"] == df["periodo"].max()]["n_empleados"].sum()

    k1,k2,k3,k4,k5,k6 = st.columns(6, gap="small")
    k1.markdown(kpi("Ventas grupo",     cop(total_ventas,1), "", True, "💰"), unsafe_allow_html=True)
    k2.markdown(kpi("Margen bruto",     cop(total_margen,1), pct(pct_margen)+" del grupo", pct_margen>30, "📊"), unsafe_allow_html=True)
    k3.markdown(kpi("EBITDA",           cop(total_ebitda,1), pct(pct_ebitda)+" del grupo", pct_ebitda>12, "📈"), unsafe_allow_html=True)
    k4.markdown(kpi("Cartera total",    cop(cartera_act,1),  "", True, "📋"), unsafe_allow_html=True)
    k5.markdown(kpi("Empleados grupo",  str(int(n_emp_act)), "", True, "👥"), unsafe_allow_html=True)
    k6.markdown(kpi("Empresas activas", "3", "CIMPA · Confía · Vasanico", True, "🏢"), unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    c1,c2 = st.columns([1.6,1], gap="medium")

    with c1:
        fig = go.Figure()
        colores = {e:c for e,c in zip(["CIMPA","Confía Control","Vasanico"],[PURPLE,TEAL,AMBER])}
        for emp in df["empresa"].unique():
            sub = df[df["empresa"]==emp].sort_values("periodo")
            fig.add_trace(go.Bar(name=emp, x=sub["periodo"].dt.strftime("%Y-%m"),
                y=sub["ventas_cop"], marker_color=colores.get(emp, SKY),
                hovertemplate=f"<b>{emp}</b><br>%{{customdata}}<extra></extra>",
                customdata=[cop(v,1) for v in sub["ventas_cop"]]))
        fig.update_layout(barmode="stack")
        st.plotly_chart(dark(fig, 330, "Ventas mensuales por empresa (COP)"), use_container_width=True)

    with c2:
        # Share of revenues last period
        ult = df[df["periodo"] == df["periodo"].max()]
        if len(ult) == 0: ult = df
        emp_share = ult.groupby("empresa")["ventas_cop"].sum().reset_index()
        fig = go.Figure(go.Pie(labels=emp_share["empresa"], values=emp_share["ventas_cop"],
            hole=0.5, marker_colors=list(colores.values()), textinfo="label+percent", textfont_size=11))
        st.plotly_chart(dark(fig, 330, "Participación en ingresos (último mes)"), use_container_width=True)

    c3,c4,c5 = st.columns(3, gap="medium")

    with c3:
        fig = go.Figure()
        for emp in df["empresa"].unique():
            sub = df[df["empresa"]==emp].sort_values("periodo")
            sub["margen_pct"] = sub["margen_bruto_cop"] / sub["ventas_cop"].replace(0,1) * 100
            fig.add_trace(go.Scatter(name=emp, x=sub["periodo"].dt.strftime("%Y-%m"),
                y=sub["margen_pct"], mode="lines+markers",
                line=dict(color=colores.get(emp,SKY), width=2),
                hovertemplate=f"<b>{emp}</b><br>%{{y:.1f}}%<extra></extra>"))
        fig.add_hline(y=30, line_dash="dash", line_color=AMBER, opacity=0.5, annotation_text="Meta 30%")
        st.plotly_chart(dark(fig, 300, "Margen bruto % por empresa"), use_container_width=True)

    with c4:
        fig = go.Figure()
        for emp in df["empresa"].unique():
            sub = df[df["empresa"]==emp].sort_values("periodo")
            sub["ebitda_pct"] = sub["ebitda_cop"] / sub["ventas_cop"].replace(0,1) * 100
            fig.add_trace(go.Scatter(name=emp, x=sub["periodo"].dt.strftime("%Y-%m"),
                y=sub["ebitda_pct"], mode="lines+markers",
                line=dict(color=colores.get(emp,SKY), width=2),
                hovertemplate=f"<b>{emp}</b><br>%{{y:.1f}}%<extra></extra>"))
        fig.add_hline(y=12, line_dash="dash", line_color=GREEN, opacity=0.5, annotation_text="Meta 12%")
        st.plotly_chart(dark(fig, 300, "EBITDA % por empresa"), use_container_width=True)

    with c5:
        cg = df.groupby("empresa")["cartera_cop"].mean().reset_index()
        fig = go.Figure(go.Bar(x=cg["empresa"], y=cg["cartera_cop"],
            marker_color=[colores.get(e,SKY) for e in cg["empresa"]],
            hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v,1) for v in cg["cartera_cop"]]))
        st.plotly_chart(dark(fig, 300, "Cartera promedio por empresa (COP)"), use_container_width=True)

    # Tabla comparativa
    st.markdown(f"<p style='font-weight:700;font-size:14px;color:{TEXT};margin-top:8px'>Comparativo anual por empresa</p>", unsafe_allow_html=True)
    anual = df.groupby(["empresa", df["periodo"].dt.year.rename("año")]).agg(
        ventas=("ventas_cop","sum"), margen=("margen_bruto_cop","sum"),
        ebitda=("ebitda_cop","sum"), cartera=("cartera_cop","mean"),
        empleados=("n_empleados","mean")
    ).reset_index()
    anual["margen_pct"] = (anual["margen"] / anual["ventas"].replace(0,1) * 100).round(1).astype(str) + "%"
    anual["ebitda_pct"] = (anual["ebitda"] / anual["ventas"].replace(0,1) * 100).round(1).astype(str) + "%"
    anual["ventas"]   = anual["ventas"].apply(cop)
    anual["margen"]   = anual["margen"].apply(cop)
    anual["ebitda"]   = anual["ebitda"].apply(cop)
    anual["cartera"]  = anual["cartera"].apply(cop)
    anual["empleados"] = anual["empleados"].round(0).astype(int)
    st.dataframe(anual.rename(columns={
        "empresa":"Empresa","año":"Año","ventas":"Ventas","margen":"Margen bruto",
        "margen_pct":"Margen %","ebitda":"EBITDA","ebitda_pct":"EBITDA %",
        "cartera":"Cartera prom","empleados":"Empleados"}).sort_values(["Empresa","Año"]),
        hide_index=True, use_container_width=True, height=300)
