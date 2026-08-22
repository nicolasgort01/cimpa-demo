import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    oc  = pd.read_csv(DATA/"ordenes_compra.csv")
    oc["fecha_orden"]            = pd.to_datetime(oc["fecha_orden"])
    oc["fecha_entrega_esperada"] = pd.to_datetime(oc["fecha_entrega_esperada"])
    oc["fecha_entrega_real"]     = pd.to_datetime(oc["fecha_entrega_real"], errors="coerce")
    inv = pd.read_csv(DATA/"inventario.csv")
    pr  = pd.read_csv(DATA/"proveedores.csv")
    return oc, inv, pr

def render():
    oc, inv, pr = load()
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">C</div>
      <div>
        <div class="cb-title">Proveedores & Compras</div>
        <div class="cb-sub">Órdenes de compra · Lead time · Evaluación de proveedores</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    f1,f2,f3 = st.columns(3)
    with f1:
        paises = ["Todos"] + sorted(oc["pais_origen"].unique().tolist())
        pais_sel = st.selectbox("País origen", paises, key="pr_pais")
    with f2:
        cats = ["Todas"] + sorted(oc["categoria"].unique().tolist())
        cat_sel = st.selectbox("Categoría", cats, key="pr_cat")
    with f3:
        estados = ["Todos"] + sorted(oc["estado"].unique().tolist())
        est_sel = st.selectbox("Estado OC", estados, key="pr_est")

    df = oc.copy()
    if pais_sel != "Todos": df = df[df["pais_origen"] == pais_sel]
    if cat_sel  != "Todas": df = df[df["categoria"]  == cat_sel]
    if est_sel  != "Todos": df = df[df["estado"]      == est_sel]

    entregadas = df[df["estado"] == "Recibida"]
    total_oc   = len(df)
    valor_oc   = df["valor_usd"].sum()
    valor_cop_oc = df["valor_cop"].sum()
    n_prov     = df["proveedor"].nunique()
    lead_prom  = entregadas["lead_time_dias"].mean() if len(entregadas) else 0
    oc_pend    = (df["estado"] == "En tránsito").sum() + (df["estado"] == "Confirmada").sum()

    k1,k2,k3,k4,k5,k6 = st.columns(6, gap="small")
    k1.markdown(kpi("Órdenes de compra", str(total_oc), "", True, "📋"), unsafe_allow_html=True)
    k2.markdown(kpi("Valor compras (USD)", f"${valor_oc/1_000_000:.2f}M", "", True, "💵"), unsafe_allow_html=True)
    k3.markdown(kpi("Valor compras (COP)", cop(valor_cop_oc,1), "", True, "💰"), unsafe_allow_html=True)
    k4.markdown(kpi("Proveedores activos", str(n_prov), "", True, "🌐"), unsafe_allow_html=True)
    k5.markdown(kpi("Lead time promedio", f"{lead_prom:.0f} días", "", lead_prom<45, "📅"), unsafe_allow_html=True)
    k6.markdown(kpi("OC pendientes", str(oc_pend), "En tránsito + confirmadas", oc_pend<10, "⏳"), unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3, gap="medium")

    with c1:
        pv = df.groupby("proveedor")["valor_usd"].sum().nlargest(10).reset_index().sort_values("valor_usd")
        fig = go.Figure(go.Bar(x=pv["valor_usd"], y=pv["proveedor"], orientation="h",
            marker_color=PALETTE[:len(pv)],
            hovertemplate="<b>%{y}</b><br>USD %{x:,.0f}<extra></extra>"))
        st.plotly_chart(dark(fig, 320, "Top 10 proveedores por valor (USD)"), use_container_width=True)

    with c2:
        pc = df.groupby("pais_origen")["valor_usd"].sum().reset_index().sort_values("valor_usd",ascending=False)
        fig = go.Figure(go.Pie(labels=pc["pais_origen"], values=pc["valor_usd"],
            hole=0.5, marker_colors=PALETTE, textinfo="label+percent", textfont_size=11))
        st.plotly_chart(dark(fig, 320, "Compras por país de origen (USD)"), use_container_width=True)

    with c3:
        cat_val = df.groupby("categoria")["valor_usd"].sum().reset_index().sort_values("valor_usd",ascending=False)
        fig = go.Figure(go.Bar(x=cat_val["categoria"], y=cat_val["valor_usd"],
            marker_color=PALETTE[:len(cat_val)],
            hovertemplate="<b>%{x}</b><br>USD %{y:,.0f}<extra></extra>"))
        st.plotly_chart(dark(fig, 320, "Valor de compras por categoría (USD)"), use_container_width=True)

    c4,c5 = st.columns(2, gap="medium")
    with c4:
        lt = entregadas.groupby("proveedor")["lead_time_dias"].mean().reset_index().sort_values("lead_time_dias",ascending=False).head(12)
        fig = go.Figure(go.Bar(x=lt["lead_time_dias"], y=lt["proveedor"], orientation="h",
            marker_color=[RED if v>60 else AMBER if v>30 else GREEN for v in lt["lead_time_dias"]],
            hovertemplate="<b>%{y}</b><br>Lead time: %{x:.0f} días<extra></extra>"))
        fig.add_vline(x=45, line_dash="dash", line_color=AMBER, opacity=0.6,
                      annotation_text="Meta 45d", annotation_font_color=AMBER)
        st.plotly_chart(dark(fig, 320, "Lead time promedio por proveedor (días)"), use_container_width=True)

    with c5:
        # Evaluación de proveedores: score compuesto
        pr_eval = pr.copy()
        fig = go.Figure()
        for col, color, name in [
            ("score_calidad", GREEN, "Calidad"),
            ("score_puntualidad", TEAL, "Puntualidad"),
            ("score_precio", PURPLE, "Precio"),
        ]:
            if col in pr_eval.columns:
                pr_sort = pr_eval.sort_values("score_general", ascending=False).head(10)
                fig.add_trace(go.Bar(name=name, x=pr_sort["proveedor"], y=pr_sort[col], marker_color=color))
        fig.update_layout(barmode="group")
        fig.update_xaxes(tickangle=-35)
        st.plotly_chart(dark(fig, 320, "Evaluación de proveedores (score 1–10)"), use_container_width=True)

    # Tabla proveedores
    st.markdown(f"<p style='font-weight:700;font-size:14px;color:{TEXT};margin-top:8px'>Detalle de órdenes de compra</p>", unsafe_allow_html=True)
    disp = df.sort_values("fecha_orden", ascending=False).copy()
    disp["valor_usd"]  = disp["valor_usd"].apply(lambda x: f"${x:,.0f}")
    disp["valor_cop"]  = disp["valor_cop"].apply(cop)
    disp["fecha_orden"] = disp["fecha_orden"].dt.strftime("%Y-%m-%d")
    disp["fecha_entrega_esperada"] = disp["fecha_entrega_esperada"].dt.strftime("%Y-%m-%d")
    st.dataframe(disp[["oc_id","proveedor","pais_origen","categoria","fecha_orden","fecha_entrega_esperada",
                        "lead_time_dias","valor_usd","valor_cop","estado"]].rename(columns={
        "oc_id":"OC","proveedor":"Proveedor","pais_origen":"País","categoria":"Categoría",
        "fecha_orden":"F. Orden","fecha_entrega_esperada":"F. Esperada","lead_time_dias":"Lead time",
        "valor_usd":"Valor USD","valor_cop":"Valor COP","estado":"Estado"}),
        hide_index=True, use_container_width=True, height=360)
