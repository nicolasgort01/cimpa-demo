import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    return pd.read_csv(DATA/"empleados.csv")

def render():
    e = load()
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">C</div>
      <div>
        <div class="cb-title">Talento Humano</div>
        <div class="cb-sub">110 empleados · Masa salarial · Ausentismo · Desempeño</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    f1,f2,f3 = st.columns(3)
    with f1:
        sedes = ["Todas"] + sorted(e["sede"].unique().tolist())
        sede_sel = st.selectbox("Sede", sedes, key="th_sede")
    with f2:
        depts = ["Todos"] + sorted(e["departamento"].unique().tolist())
        dept_sel = st.selectbox("Departamento", depts, key="th_dept")
    with f3:
        cargos = ["Todos"] + sorted(e["tipo_contrato"].unique().tolist())
        cargo_sel = st.selectbox("Tipo contrato", cargos, key="th_cont")

    df = e.copy()
    if sede_sel != "Todas": df = df[df["sede"] == sede_sel]
    if dept_sel != "Todos": df = df[df["departamento"] == dept_sel]
    if cargo_sel!= "Todos": df = df[df["tipo_contrato"] == cargo_sel]

    n_emp       = len(df)
    masa_sal    = df["salario_cop"].sum()
    sal_prom    = df["salario_cop"].mean()
    ausent_prom = df["dias_ausentismo"].mean()
    rot_pct     = (df["estado"] == "Inactivo").sum() / len(e) * 100
    perf_prom   = df["score_desempeno"].mean()
    antiguedad  = df["antiguedad_anos"].mean()

    k1,k2,k3,k4,k5,k6 = st.columns(6, gap="small")
    k1.markdown(kpi("Total empleados",    str(n_emp),         "", True, "👥"), unsafe_allow_html=True)
    k2.markdown(kpi("Masa salarial/mes",  cop(masa_sal,1),    "", True, "💰"), unsafe_allow_html=True)
    k3.markdown(kpi("Salario promedio",   cop(sal_prom),      "", True, "📊"), unsafe_allow_html=True)
    k4.markdown(kpi("Ausentismo prom",    f"{ausent_prom:.1f} días", "últimos 12 meses", ausent_prom<5, "🏥"), unsafe_allow_html=True)
    k5.markdown(kpi("Score desempeño",    f"{perf_prom:.1f}/10", "", perf_prom>7, "⭐"), unsafe_allow_html=True)
    k6.markdown(kpi("Antigüedad prom",    f"{antiguedad:.1f} años", "", True, "🗓️"), unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3, gap="medium")

    with c1:
        dept_cnt = df.groupby("departamento").size().reset_index(name="n").sort_values("n",ascending=False)
        fig = go.Figure(go.Pie(labels=dept_cnt["departamento"], values=dept_cnt["n"],
            hole=0.5, marker_colors=PALETTE, textinfo="label+value", textfont_size=11))
        st.plotly_chart(dark(fig, 310, "Empleados por departamento"), use_container_width=True)

    with c2:
        sede_sal = df.groupby("sede")["salario_cop"].sum().reset_index().sort_values("salario_cop",ascending=True)
        fig = go.Figure(go.Bar(x=sede_sal["salario_cop"], y=sede_sal["sede"], orientation="h",
            marker_color=PALETTE[:len(sede_sal)],
            hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v,1) for v in sede_sal["salario_cop"]]))
        st.plotly_chart(dark(fig, 310, "Masa salarial mensual por sede (COP)"), use_container_width=True)

    with c3:
        cont_cnt = df.groupby("tipo_contrato").size().reset_index(name="n")
        fig = go.Figure(go.Pie(labels=cont_cnt["tipo_contrato"], values=cont_cnt["n"],
            hole=0.5, marker_colors=[PURPLE, TEAL, AMBER, GREEN], textinfo="label+percent", textfont_size=11))
        st.plotly_chart(dark(fig, 310, "Empleados por tipo de contrato"), use_container_width=True)

    c4,c5 = st.columns(2, gap="medium")

    with c4:
        fig = go.Figure(go.Histogram(x=df["score_desempeno"], nbinsx=20,
            marker_color=PURPLE, opacity=0.85,
            hovertemplate="Score: %{x:.1f}<br>Empleados: %{y}<extra></extra>"))
        fig.add_vline(x=perf_prom, line_dash="dash", line_color=TEAL,
                      annotation_text=f"Prom {perf_prom:.1f}", annotation_font_color=TEAL)
        fig.add_vline(x=7, line_dash="dot", line_color=GREEN, opacity=0.6,
                      annotation_text="Meta 7.0", annotation_font_color=GREEN)
        st.plotly_chart(dark(fig, 290, "Distribución de score de desempeño"), use_container_width=True)

    with c5:
        dept_perf = df.groupby("departamento").agg(
            perf=("score_desempeno","mean"),
            ausent=("dias_ausentismo","mean")
        ).reset_index().sort_values("perf",ascending=False)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Score desempeño", x=dept_perf["departamento"], y=dept_perf["perf"],
            marker_color=TEAL, hovertemplate="<b>%{x}</b><br>Score: %{y:.2f}<extra></extra>"))
        fig.add_trace(go.Scatter(name="Ausentismo (días)", x=dept_perf["departamento"],
            y=dept_perf["ausent"], mode="markers+lines",
            marker=dict(color=RED, size=8), line=dict(color=RED, width=1.5, dash="dot"), yaxis="y2"))
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False,
            tickfont=dict(color=RED,size=11)))
        fig.update_xaxes(tickangle=-30)
        st.plotly_chart(dark(fig, 290, "Desempeño y ausentismo por departamento"), use_container_width=True)

    # Pirámide por género y rango de edad
    c6,c7 = st.columns(2, gap="medium")
    with c6:
        rangos = pd.cut(df["edad"], bins=[18,25,30,35,40,50,65],
                        labels=["18-25","26-30","31-35","36-40","41-50","51-65"])
        edad_cnt = df.groupby(rangos).size().reset_index(name="n")
        fig = go.Figure(go.Bar(x=edad_cnt["edad"].astype(str), y=edad_cnt["n"],
            marker_color=PALETTE[:len(edad_cnt)],
            hovertemplate="<b>%{x} años</b><br>%{y} empleados<extra></extra>"))
        st.plotly_chart(dark(fig, 280, "Distribución por rango de edad"), use_container_width=True)

    with c7:
        gen_cnt = df.groupby("genero").size().reset_index(name="n")
        fig = go.Figure(go.Pie(labels=gen_cnt["genero"], values=gen_cnt["n"],
            hole=0.5, marker_colors=[PURPLE, TEAL],
            textinfo="label+percent+value", textfont_size=12))
        st.plotly_chart(dark(fig, 280, "Distribución por género"), use_container_width=True)

    st.markdown(f"<p style='font-weight:700;font-size:14px;color:{TEXT};margin-top:8px'>Directorio de empleados</p>", unsafe_allow_html=True)
    disp = df.copy()
    disp["salario_cop"] = disp["salario_cop"].apply(cop)
    st.dataframe(disp[["nombre","sede","departamento","cargo","tipo_contrato","antiguedad_anos",
                        "salario_cop","score_desempeno","dias_ausentismo","estado"]].rename(columns={
        "nombre":"Nombre","sede":"Sede","departamento":"Dpto.","cargo":"Cargo",
        "tipo_contrato":"Contrato","antiguedad_anos":"Antigüedad (años)",
        "salario_cop":"Salario","score_desempeno":"Desempeño","dias_ausentismo":"Ausentismo","estado":"Estado"}).sort_values("Dpto."),
        hide_index=True, use_container_width=True, height=360)
