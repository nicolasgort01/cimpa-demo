import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    return pd.read_csv(DATA/"inventario.csv")

def render():
    inv = load()
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">C</div>
      <div>
        <div class="cb-title">Inventario Multi-Bodega</div>
        <div class="cb-sub">Stock en tiempo real · 7 sedes · {inv['producto_id'].nunique()} SKUs</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    # Filters
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        sedes = ["Todas las sedes"] + sorted(inv["sede_nombre"].unique().tolist())
        sede_sel = st.selectbox("Sede / Bodega", sedes, key="inv_sede")
    with f2:
        cats = ["Todas"] + sorted(inv["categoria"].unique().tolist())
        cat_sel = st.selectbox("Categoría", cats, key="inv_cat")
    with f3:
        estados = ["Todos"] + sorted(inv["estado"].unique().tolist())
        est_sel = st.selectbox("Estado de stock", estados, key="inv_est")
    with f4:
        provs = ["Todos"] + sorted(inv["proveedor"].unique().tolist())
        prov_sel = st.selectbox("Proveedor", provs, key="inv_prov")

    df = inv.copy()
    if sede_sel != "Todas las sedes": df = df[df["sede_nombre"] == sede_sel]
    if cat_sel  != "Todas":           df = df[df["categoria"]   == cat_sel]
    if est_sel  != "Todos":           df = df[df["estado"]       == est_sel]
    if prov_sel != "Todos":           df = df[df["proveedor"]    == prov_sel]

    # KPIs
    total_val   = df["valor_inventario"].sum()
    n_critico   = (df["estado"] == "Crítico").sum()
    n_bajo      = (df["estado"] == "Bajo").sum()
    n_skus      = df["producto_id"].nunique()
    cob_avg     = df["dias_cobertura"].mean()
    val_critico = df[df["estado"] == "Crítico"]["valor_inventario"].sum()

    k1,k2,k3,k4,k5,k6 = st.columns(6, gap="small")
    k1.markdown(kpi("Valor en inventario", cop(total_val,1), "", True, "💎"), unsafe_allow_html=True)
    k2.markdown(kpi("SKUs en catálogo", str(n_skus), "", True, "📦"), unsafe_allow_html=True)
    k3.markdown(kpi("Cobertura promedio", f"{cob_avg:.0f} días", "", cob_avg > 20, "📅"), unsafe_allow_html=True)
    k4.markdown(kpi("SKUs críticos", str(n_critico), "Bajo mínimo 50%", n_critico == 0, "🔴"), unsafe_allow_html=True)
    k5.markdown(kpi("SKUs en nivel bajo", str(n_bajo), "Entre mín y mín×1", n_bajo == 0, "🟡"), unsafe_allow_html=True)
    k6.markdown(kpi("Valor en riesgo", cop(val_critico,1), "En stock crítico", val_critico == 0, "⚠️"), unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # Row 1
    c1, c2 = st.columns([1.4, 1], gap="medium")

    with c1:
        val_sede = df.groupby("sede_nombre")["valor_inventario"].sum().sort_values(ascending=False).reset_index()
        fig = go.Figure(go.Bar(
            x=val_sede["sede_nombre"], y=val_sede["valor_inventario"],
            marker_color=PALETTE[:len(val_sede)],
            hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v,1) for v in val_sede["valor_inventario"]],
        ))
        st.plotly_chart(dark(fig, 300, "Valor de inventario por sede (COP)"), use_container_width=True)

    with c2:
        val_cat = df.groupby("categoria")["valor_inventario"].sum().reset_index()
        fig = go.Figure(go.Pie(
            labels=val_cat["categoria"], values=val_cat["valor_inventario"],
            hole=0.5, marker_colors=PALETTE,
            textinfo="label+percent", textfont_size=11,
            hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v,1) for v in val_cat["valor_inventario"]],
        ))
        st.plotly_chart(dark(fig, 300, "Distribución por categoría"), use_container_width=True)

    # Row 2
    c3, c4 = st.columns(2, gap="medium")

    with c3:
        estado_cnt = df.groupby(["categoria","estado"]).size().reset_index(name="n")
        fig = go.Figure()
        for est, col in [("Crítico",RED),("Bajo",AMBER),("Normal",GREEN),("Alto",SKY)]:
            sub = estado_cnt[estado_cnt["estado"]==est]
            if not sub.empty:
                fig.add_trace(go.Bar(name=est, x=sub["categoria"], y=sub["n"], marker_color=col))
        fig.update_layout(barmode="stack")
        st.plotly_chart(dark(fig, 300, "SKUs por estado y categoría"), use_container_width=True)

    with c4:
        rot = df.groupby("categoria").agg(
            stock=("stock_actual","sum"), min_stock=("stock_minimo","sum")
        ).reset_index()
        rot["rotacion_idx"] = (rot["stock"] / rot["min_stock"].replace(0,1)).round(1)
        fig = go.Figure(go.Bar(
            x=rot["rotacion_idx"], y=rot["categoria"], orientation="h",
            marker_color=[GREEN if r > 2 else AMBER if r > 1 else RED for r in rot["rotacion_idx"]],
            hovertemplate="<b>%{y}</b><br>Índice: %{x:.1f}x<extra></extra>",
        ))
        fig.add_vline(x=1, line_dash="dash", line_color=AMBER, opacity=0.7,
                      annotation_text="Mínimo", annotation_font_color=AMBER)
        st.plotly_chart(dark(fig, 300, "Índice vs. stock mínimo por categoría"), use_container_width=True)

    # Detailed table
    st.markdown(f"<div style='height:8px'></div><p style='font-weight:700;font-size:14px;color:{TEXT}'>Detalle por producto y sede</p>", unsafe_allow_html=True)

    disp = df[["sede_nombre","categoria","producto","unidad","stock_actual","stock_minimo","dias_cobertura","valor_inventario","proveedor","estado"]].copy()
    disp["valor_inventario"] = disp["valor_inventario"].apply(cop)

    def color_estado(val):
        c = estado_color(val)
        return f"color:{c};font-weight:700"

    st.dataframe(
        disp.sort_values(["estado","sede_nombre"]).rename(columns={
            "sede_nombre":"Sede","categoria":"Categoría","producto":"Producto",
            "unidad":"Unidad","stock_actual":"Stock actual","stock_minimo":"Mínimo",
            "dias_cobertura":"Días cob.","valor_inventario":"Valor inv.","proveedor":"Proveedor","estado":"Estado"
        }),
        hide_index=True, use_container_width=True, height=380,
    )
