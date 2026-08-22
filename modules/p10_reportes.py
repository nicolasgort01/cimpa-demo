import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    v   = pd.read_csv(DATA/"ventas.csv")
    v["fecha"] = pd.to_datetime(v["fecha"])

    c   = pd.read_csv(DATA/"cartera.csv")
    c["fecha_factura"]    = pd.to_datetime(c["fecha_factura"])
    c["fecha_vencimiento"] = pd.to_datetime(c["fecha_vencimiento"])

    inv = pd.read_csv(DATA/"inventario.csv")

    d   = pd.read_csv(DATA/"despachos.csv")
    d["fecha_pedido"]             = pd.to_datetime(d["fecha_pedido"])
    d["fecha_entrega_prometida"]  = pd.to_datetime(d["fecha_entrega_prometida"])
    d["fecha_entrega_real"]       = pd.to_datetime(d["fecha_entrega_real"], errors="coerce")

    emp = pd.read_csv(DATA/"empleados.csv")

    g   = pd.read_csv(DATA/"grupo_mensual.csv")
    g["periodo"] = pd.to_datetime(g["periodo"])

    return v, c, inv, d, emp, g

HOY = date(2026, 8, 22)
HOY_STR = "22 de agosto de 2026"

STYLE = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  * {{ box-sizing:border-box; margin:0; padding:0 }}
  body {{ font-family:'Inter',Arial,sans-serif; background:#fff; color:#1a1a2e; font-size:13px; line-height:1.5 }}
  .rpt-page {{ max-width:900px; margin:0 auto; padding:32px }}
  .rpt-header {{ display:flex; align-items:center; gap:16px; padding-bottom:20px;
    border-bottom:3px solid #6c63ff; margin-bottom:24px }}
  .rpt-logo {{ width:48px; height:48px; border-radius:12px;
    background:linear-gradient(135deg,#6c63ff,#3ecfcf);
    display:flex; align-items:center; justify-content:center;
    font-size:24px; font-weight:900; color:#fff }}
  .rpt-company {{ flex:1 }}
  .rpt-company h1 {{ font-size:22px; font-weight:800; color:#1a1a2e }}
  .rpt-company p {{ font-size:12px; color:#7e7e96; margin-top:2px }}
  .rpt-meta {{ text-align:right; font-size:11px; color:#7e7e96 }}
  .rpt-meta strong {{ color:#6c63ff; font-size:14px; display:block; margin-bottom:2px }}
  .rpt-title {{ font-size:18px; font-weight:800; color:#6c63ff;
    margin:0 0 20px; padding:12px 16px; background:#f5f4ff;
    border-left:4px solid #6c63ff; border-radius:0 8px 8px 0 }}
  .kpi-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:24px }}
  .kpi-box {{ background:#f8f8ff; border:1px solid #e8e7ff; border-radius:10px; padding:16px }}
  .kpi-label {{ font-size:10px; text-transform:uppercase; letter-spacing:.08em; color:#7e7e96; margin-bottom:6px }}
  .kpi-val {{ font-size:22px; font-weight:800; color:#1a1a2e; line-height:1 }}
  .kpi-delta {{ font-size:11px; margin-top:4px }}
  .kpi-good {{ color:#22c55e }} .kpi-bad {{ color:#ef4444 }}
  .section-title {{ font-size:13px; font-weight:700; color:#6c63ff; margin:20px 0 10px;
    text-transform:uppercase; letter-spacing:.06em }}
  table {{ width:100%; border-collapse:collapse; font-size:12px; margin-bottom:16px }}
  thead th {{ background:#6c63ff; color:#fff; padding:8px 10px; text-align:left;
    font-size:11px; font-weight:600; letter-spacing:.04em }}
  tbody tr:nth-child(even) td {{ background:#f8f8ff }}
  tbody td {{ padding:7px 10px; border-bottom:1px solid #eeeef8 }}
  .tag-red {{ background:#fef2f2; color:#ef4444; padding:2px 8px; border-radius:99px; font-size:10px; font-weight:600 }}
  .tag-amber {{ background:#fffbeb; color:#f59e0b; padding:2px 8px; border-radius:99px; font-size:10px; font-weight:600 }}
  .tag-green {{ background:#f0fdf4; color:#22c55e; padding:2px 8px; border-radius:99px; font-size:10px; font-weight:600 }}
  .tag-blue {{ background:#eff6ff; color:#3b82f6; padding:2px 8px; border-radius:99px; font-size:10px; font-weight:600 }}
  .alert-box {{ background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:14px 16px; margin-bottom:16px }}
  .alert-box h4 {{ color:#ef4444; font-size:12px; margin-bottom:8px }}
  .rpt-footer {{ margin-top:32px; padding-top:16px; border-top:1px solid #eeeef8;
    display:flex; justify-content:space-between; font-size:10px; color:#b0b0c0 }}
  .page-break {{ page-break-before:always; margin-top:32px }}
  .print-note {{ background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px;
    padding:10px 14px; margin-bottom:20px; font-size:11px; color:#166534 }}
  @media print {{
    .print-note {{ display:none }}
    body {{ font-size:12px }}
    .rpt-page {{ padding:16px }}
  }}
</style>"""

HEADER_HTML = f"""
<div class="rpt-header">
  <div class="rpt-logo">C</div>
  <div class="rpt-company">
    <h1>CIMPA S.A.S.</h1>
    <p>Av. Américas No. 63-05 · Bogotá, Colombia · 30 años de experiencia</p>
  </div>
  <div class="rpt-meta">
    <strong>Panel de Inteligencia de Negocios</strong>
    Generado: {HOY_STR}<br>
    <span style="color:#3ecfcf;font-size:10px">Powered by Calybrat</span>
  </div>
</div>"""

FOOTER_HTML = """
<div class="rpt-footer">
  <span>CIMPA S.A.S. · Confidencial</span>
  <span>Generado automáticamente por Calybrat BI · 2026</span>
</div>"""

def kpi_box(label, val, delta="", good=True):
    d = f'<div class="kpi-delta {"kpi-good" if good else "kpi-bad"}">{delta}</div>' if delta else ""
    return f'<div class="kpi-box"><div class="kpi-label">{label}</div><div class="kpi-val">{val}</div>{d}</div>'

def tag(text, color="blue"):
    return f'<span class="tag-{color}">{text}</span>'

def build_ejecutivo(v, c, inv, d, g):
    v26 = v[v["fecha"].dt.year == 2026]
    v25 = v[v["fecha"].dt.year == 2025]
    total26 = v26["total_cop"].sum(); total25 = v25["total_cop"].sum()
    crecimiento = (total26 - total25) / total25 * 100 if total25 else 0
    vencida = c[c["dias_mora"]>0]["valor_cop"].sum()
    pct_venc = vencida/c["valor_cop"].sum()*100 if c["valor_cop"].sum() else 0
    criticos = inv[inv["estado"]=="Crítico"].shape[0]
    bajos    = inv[inv["estado"]=="Bajo"].shape[0]
    ent = d[d["estado"]=="Entregado"]
    otd = (ent["entregado_a_tiempo"]==True).sum()/len(ent)*100 if len(ent) else 0
    margen = v26["margen_pct"].mean()*100 if len(v26) else 0

    ventas_mes = v26.groupby(v26["fecha"].dt.to_period("M").astype(str))["total_cop"].sum().tail(3)
    ventas_tabla = "".join([f"<tr><td>{m}</td><td style='text-align:right'>{cop(s,1)}</td></tr>" for m,s in ventas_mes.items()])

    top_cli = v26.groupby("cliente")["total_cop"].sum().nlargest(5).reset_index()
    cli_tabla = "".join([f"<tr><td>{r['cliente']}</td><td style='text-align:right'>{cop(r['total_cop'],1)}</td></tr>" for _,r in top_cli.iterrows()])

    cat_ventas = v26.groupby("categoria")["total_cop"].sum().sort_values(ascending=False)
    cat_tabla = "".join([f"<tr><td>{cat}</td><td style='text-align:right'>{cop(v,1)}</td><td style='text-align:right'>{v/total26*100:.1f}%</td></tr>" for cat,v in cat_ventas.items()])

    # Grupo last 3 months
    g3 = g.sort_values("periodo").tail(9)
    g_tabla = "".join([
        f"<tr><td>{r['empresa']}</td><td style='text-align:right'>{cop(r['ventas_cop'],1)}</td>"
        f"<td style='text-align:right'>{r['ventas_cop']/r['ventas_cop']*0+r['margen_bruto_cop']/r['ventas_cop']*100:.1f}%</td>"
        f"<td style='text-align:right'>{cop(r['ebitda_cop'],1)}</td></tr>"
        for _,r in g3.groupby("empresa").agg(ventas_cop=("ventas_cop","sum"),margen_bruto_cop=("margen_bruto_cop","sum"),ebitda_cop=("ebitda_cop","sum")).reset_index().iterrows()
    ])

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Reporte Ejecutivo Mensual — CIMPA</title>{STYLE}</head><body>
    <div class="rpt-page">
      <div class="print-note">💡 Para guardar como PDF: <strong>Ctrl+P → Guardar como PDF</strong></div>
      {HEADER_HTML}
      <div class="rpt-title">📊 Reporte Ejecutivo Mensual — Agosto 2026</div>

      <div class="kpi-grid">
        {kpi_box("Ventas 2026 YTD", cop(total26,1), f"{'▲' if crecimiento>=0 else '▼'} {abs(crecimiento):.1f}% vs 2025", crecimiento>=0)}
        {kpi_box("Margen bruto", pct(margen), "Promedio período", margen>30)}
        {kpi_box("Cartera vencida", cop(vencida,1), f"{pct_venc:.1f}% del total", pct_venc<15)}
        {kpi_box("SKUs críticos", str(criticos), f"{bajos} en nivel bajo", criticos==0)}
        {kpi_box("OTD despachos", pct(otd), f"Meta: 85%", otd>=85)}
        {kpi_box("Clientes activos", str(v26['cliente_id'].nunique()), "Período 2026", True)}
      </div>

      <div class="section-title">Ventas últimos 3 meses</div>
      <table><thead><tr><th>Período</th><th style="text-align:right">Ventas COP</th></tr></thead>
      <tbody>{ventas_tabla}</tbody></table>

      <div class="section-title">Top 5 clientes 2026 YTD</div>
      <table><thead><tr><th>Cliente</th><th style="text-align:right">Ventas COP</th></tr></thead>
      <tbody>{cli_tabla}</tbody></table>

      <div class="section-title">Ventas por categoría 2026 YTD</div>
      <table><thead><tr><th>Categoría</th><th style="text-align:right">Ventas COP</th><th style="text-align:right">Part. %</th></tr></thead>
      <tbody>{cat_tabla}</tbody></table>

      <div class="section-title">Consolidado del Grupo Empresarial</div>
      <table><thead><tr><th>Empresa</th><th style="text-align:right">Ventas</th><th style="text-align:right">Margen %</th><th style="text-align:right">EBITDA</th></tr></thead>
      <tbody>{g_tabla}</tbody></table>
      {FOOTER_HTML}
    </div></body></html>"""


def build_ventas(v, sede_sel, cat_sel):
    df = v[v["fecha"].dt.year == 2026].copy()
    if sede_sel != "Todas": df = df[df["sede_id"] == sede_sel]
    if cat_sel  != "Todas": df = df[df["categoria"] == cat_sel]

    total = df["total_cop"].sum()
    n_cli = df["cliente_id"].nunique()
    ticket = total / len(df) if len(df) else 0
    margen = df["margen_pct"].mean()*100 if len(df) else 0

    top10 = df.groupby(["cliente","sector_cliente"]).agg(
        ventas=("total_cop","sum"), ordenes=("total_cop","count"), margen=("margen_pct","mean")
    ).reset_index().nlargest(10,"ventas")
    rows_cli = "".join([
        f"<tr><td>{r['cliente']}</td><td>{r['sector_cliente']}</td>"
        f"<td style='text-align:right'>{cop(r['ventas'],1)}</td>"
        f"<td style='text-align:right'>{int(r['ordenes'])}</td>"
        f"<td style='text-align:right'>{r['margen']*100:.1f}%</td></tr>"
        for _,r in top10.iterrows()])

    top_prod = df.groupby(["producto","categoria"])["total_cop"].sum().nlargest(10).reset_index()
    rows_prod = "".join([
        f"<tr><td>{r['producto']}</td><td>{r['categoria']}</td>"
        f"<td style='text-align:right'>{cop(r['total_cop'],1)}</td>"
        f"<td style='text-align:right'>{r['total_cop']/total*100:.1f}%</td></tr>"
        for _,r in top_prod.iterrows()])

    sede_det = df.groupby("sede_id").agg(ventas=("total_cop","sum"),ordenes=("total_cop","count")).reset_index().sort_values("ventas",ascending=False)
    rows_sede = "".join([f"<tr><td>{r['sede_id']}</td><td style='text-align:right'>{cop(r['ventas'],1)}</td><td style='text-align:right'>{int(r['ordenes'])}</td><td style='text-align:right'>{r['ventas']/total*100:.1f}%</td></tr>" for _,r in sede_det.iterrows()])

    filtros = f"Sede: {sede_sel} · Categoría: {cat_sel}"
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Reporte de Ventas — CIMPA</title>{STYLE}</head><body>
    <div class="rpt-page">
      <div class="print-note">💡 Para guardar como PDF: <strong>Ctrl+P → Guardar como PDF</strong></div>
      {HEADER_HTML}
      <div class="rpt-title">💰 Reporte de Ventas y Clientes — 2026 YTD</div>
      <p style="font-size:11px;color:#7e7e96;margin-bottom:16px">Filtros: {filtros}</p>
      <div class="kpi-grid">
        {kpi_box("Ventas totales", cop(total,1), "", True)}
        {kpi_box("Clientes activos", str(n_cli), "", True)}
        {kpi_box("Ticket promedio", cop(ticket), "", True)}
        {kpi_box("Margen bruto prom", pct(margen), "Meta: 30%", margen>=30)}
        {kpi_box("Órdenes", f"{len(df):,}", "", True)}
        {kpi_box("Categorías activas", str(df['categoria'].nunique()), "", True)}
      </div>
      <div class="section-title">Top 10 clientes por ingresos</div>
      <table><thead><tr><th>Cliente</th><th>Sector</th><th style="text-align:right">Ventas COP</th><th style="text-align:right">Órdenes</th><th style="text-align:right">Margen</th></tr></thead>
      <tbody>{rows_cli}</tbody></table>
      <div class="section-title">Top 10 productos más vendidos</div>
      <table><thead><tr><th>Producto</th><th>Categoría</th><th style="text-align:right">Ventas COP</th><th style="text-align:right">Part. %</th></tr></thead>
      <tbody>{rows_prod}</tbody></table>
      <div class="section-title">Detalle por sede</div>
      <table><thead><tr><th>Sede</th><th style="text-align:right">Ventas COP</th><th style="text-align:right">Órdenes</th><th style="text-align:right">Part. %</th></tr></thead>
      <tbody>{rows_sede}</tbody></table>
      {FOOTER_HTML}
    </div></body></html>"""


def build_cartera(c):
    total = c["valor_cop"].sum()
    vencida = c[c["dias_mora"]>0]["valor_cop"].sum()
    critica = c[c["dias_mora"]>90]["valor_cop"].sum()

    buckets = {
        "Vigente":       c[c["dias_mora"]==0]["valor_cop"].sum(),
        "Vencida 1-30d": c[c["dias_mora"].between(1,30)]["valor_cop"].sum(),
        "Vencida 31-60d":c[c["dias_mora"].between(31,60)]["valor_cop"].sum(),
        "Vencida 61-90d":c[c["dias_mora"].between(61,90)]["valor_cop"].sum(),
        "Vencida +90d":  c[c["dias_mora"]>90]["valor_cop"].sum(),
    }
    colores_bucket = {"Vigente":"green","Vencida 1-30d":"amber","Vencida 31-60d":"amber","Vencida 61-90d":"red","Vencida +90d":"red"}
    rows_aging = "".join([
        f"<tr><td>{k}</td><td style='text-align:right'>{cop(v,1)}</td>"
        f"<td style='text-align:right'>{v/total*100:.1f}%</td>"
        f"<td>{tag(k.split()[0], colores_bucket[k])}</td></tr>"
        for k,v in buckets.items()])

    mora_det = c[c["dias_mora"]>0].sort_values("dias_mora",ascending=False).head(15)
    rows_mora = "".join([
        f"<tr><td>{r['factura_id']}</td><td>{r['cliente']}</td>"
        f"<td style='text-align:right'>{cop(r['valor_cop'],1)}</td>"
        f"<td style='text-align:right;font-weight:700;color:{'#ef4444' if r['dias_mora']>60 else '#f59e0b'}'>{int(r['dias_mora'])} días</td>"
        f"<td>{r['fecha_vencimiento'].strftime('%Y-%m-%d')}</td>"
        f"<td>{tag(r['estado'], 'red' if r['dias_mora']>60 else 'amber')}</td></tr>"
        for _,r in mora_det.iterrows()])

    por_sector = c.groupby("sector")["valor_cop"].sum().reset_index().sort_values("valor_cop",ascending=False)
    rows_sec = "".join([f"<tr><td>{r['sector']}</td><td style='text-align:right'>{cop(r['valor_cop'],1)}</td><td style='text-align:right'>{r['valor_cop']/total*100:.1f}%</td></tr>" for _,r in por_sector.iterrows()])

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Reporte de Cartera — CIMPA</title>{STYLE}</head><body>
    <div class="rpt-page">
      <div class="print-note">💡 Para guardar como PDF: <strong>Ctrl+P → Guardar como PDF</strong></div>
      {HEADER_HTML}
      <div class="rpt-title">📋 Reporte de Cartera y Cobranza — {HOY_STR}</div>
      <div class="kpi-grid">
        {kpi_box("Cartera total", cop(total,1), "", True)}
        {kpi_box("Cartera vigente", cop(total-vencida,1), f"{(total-vencida)/total*100:.1f}%", True)}
        {kpi_box("Cartera vencida", cop(vencida,1), f"{vencida/total*100:.1f}% del total", vencida/total<0.15)}
        {kpi_box("Vencida +90 días", cop(critica,1), "Cartera crítica", critica==0)}
        {kpi_box("Clientes en mora", str(c[c['dias_mora']>0]['cliente'].nunique()), "", c[c['dias_mora']>0]['cliente'].nunique()==0)}
        {kpi_box("Días mora prom.", f"{c[c['dias_mora']>0]['dias_mora'].mean():.0f} días", "", False)}
      </div>
      <div class="alert-box">
        <h4>⚠️ Alertas de cobranza prioritarias</h4>
        <p>Existen <strong>{c[c['dias_mora']>90]['cliente'].nunique()} clientes</strong> con cartera vencida mayor a 90 días
        por un valor de <strong>{cop(critica,1)}</strong>. Se recomienda gestión inmediata.</p>
      </div>
      <div class="section-title">Aging de cartera</div>
      <table><thead><tr><th>Bucket</th><th style="text-align:right">Valor COP</th><th style="text-align:right">Part. %</th><th>Estado</th></tr></thead>
      <tbody>{rows_aging}</tbody></table>
      <div class="section-title">Cartera vencida por sector</div>
      <table><thead><tr><th>Sector</th><th style="text-align:right">Valor COP</th><th style="text-align:right">Part. %</th></tr></thead>
      <tbody>{rows_sec}</tbody></table>
      <div class="section-title">Facturas en mora (top 15 por antigüedad)</div>
      <table><thead><tr><th>Factura</th><th>Cliente</th><th style="text-align:right">Valor</th><th style="text-align:right">Días mora</th><th>Vencimiento</th><th>Estado</th></tr></thead>
      <tbody>{rows_mora}</tbody></table>
      {FOOTER_HTML}
    </div></body></html>"""


def build_inventario(inv):
    crit = inv[inv["estado"]=="Crítico"].sort_values("stock_actual")
    bajos = inv[inv["estado"]=="Bajo"].sort_values("dias_cobertura")
    total_val = inv["valor_inventario"].sum()

    rows_crit = "".join([
        f"<tr><td>{r['producto']}</td><td>{r['categoria']}</td><td>{r['sede_nombre']}</td>"
        f"<td style='text-align:right;font-weight:700;color:#ef4444'>{r['stock_actual']:.0f}</td>"
        f"<td style='text-align:right'>{r['stock_minimo']:.0f}</td>"
        f"<td style='text-align:right'>{r['dias_cobertura']:.0f}</td>"
        f"<td>{r['proveedor']}</td>"
        f"<td>{tag('CRÍTICO','red')}</td></tr>"
        for _,r in crit.head(20).iterrows()])

    rows_bajos = "".join([
        f"<tr><td>{r['producto']}</td><td>{r['categoria']}</td><td>{r['sede_nombre']}</td>"
        f"<td style='text-align:right;color:#f59e0b'>{r['stock_actual']:.0f}</td>"
        f"<td style='text-align:right'>{r['stock_minimo']:.0f}</td>"
        f"<td style='text-align:right'>{r['dias_cobertura']:.0f}</td>"
        f"<td>{tag('BAJO','amber')}</td></tr>"
        for _,r in bajos.head(15).iterrows()])

    sede_val = inv.groupby("sede_nombre")["valor_inventario"].sum().sort_values(ascending=False).reset_index()
    rows_sede = "".join([f"<tr><td>{r['sede_nombre']}</td><td style='text-align:right'>{cop(r['valor_inventario'],1)}</td><td style='text-align:right'>{r['valor_inventario']/total_val*100:.1f}%</td></tr>" for _,r in sede_val.iterrows()])

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Reporte de Inventario — CIMPA</title>{STYLE}</head><body>
    <div class="rpt-page">
      <div class="print-note">💡 Para guardar como PDF: <strong>Ctrl+P → Guardar como PDF</strong></div>
      {HEADER_HTML}
      <div class="rpt-title">📦 Reporte de Inventario Multi-Bodega — {HOY_STR}</div>
      <div class="kpi-grid">
        {kpi_box("Valor total inventario", cop(total_val,1), "7 bodegas", True)}
        {kpi_box("SKUs totales", str(inv['producto_id'].nunique()), "catálogo activo", True)}
        {kpi_box("Cobertura prom.", f"{inv['dias_cobertura'].mean():.0f} días", "", True)}
        {kpi_box("SKUs críticos", str(len(crit)), "Requieren reabastecimiento urgente", len(crit)==0)}
        {kpi_box("SKUs en nivel bajo", str(len(bajos)), "Vigilancia activa", len(bajos)==0)}
        {kpi_box("Valor en riesgo", cop(crit['valor_inventario'].sum(),1), "Stock crítico", False)}
      </div>
      <div class="alert-box">
        <h4>⚠️ Acción requerida: {len(crit)} SKUs por debajo del mínimo</h4>
        <p>Los siguientes productos tienen stock menor al 50% del mínimo requerido. Se recomienda emitir órdenes de compra de forma inmediata.</p>
      </div>
      <div class="section-title">SKUs en estado CRÍTICO</div>
      <table><thead><tr><th>Producto</th><th>Categoría</th><th>Bodega</th><th style="text-align:right">Stock</th><th style="text-align:right">Mínimo</th><th style="text-align:right">Cobertura (d)</th><th>Proveedor</th><th>Estado</th></tr></thead>
      <tbody>{rows_crit}</tbody></table>
      <div class="section-title">SKUs en nivel BAJO</div>
      <table><thead><tr><th>Producto</th><th>Categoría</th><th>Bodega</th><th style="text-align:right">Stock</th><th style="text-align:right">Mínimo</th><th style="text-align:right">Cobertura (d)</th><th>Estado</th></tr></thead>
      <tbody>{rows_bajos}</tbody></table>
      <div class="section-title">Valor de inventario por bodega</div>
      <table><thead><tr><th>Bodega</th><th style="text-align:right">Valor COP</th><th style="text-align:right">Part. %</th></tr></thead>
      <tbody>{rows_sede}</tbody></table>
      {FOOTER_HTML}
    </div></body></html>"""


def build_grupo(g):
    g["mes_str"] = g["periodo"].dt.strftime("%Y-%m")
    anual = g.groupby(["empresa",g["periodo"].dt.year.rename("año")]).agg(
        ventas=("ventas_cop","sum"), margen=("margen_bruto_cop","sum"),
        ebitda=("ebitda_cop","sum"), cartera=("cartera_cop","mean"),
        emp=("n_empleados","first")
    ).reset_index()

    rows_anual = "".join([
        f"<tr><td><strong>{r['empresa']}</strong></td><td style='text-align:right'>{int(r['año'])}</td>"
        f"<td style='text-align:right'>{cop(r['ventas'],1)}</td>"
        f"<td style='text-align:right'>{r['margen']/r['ventas']*100:.1f}%</td>"
        f"<td style='text-align:right'>{r['ebitda']/r['ventas']*100:.1f}%</td>"
        f"<td style='text-align:right'>{cop(r['cartera'],1)}</td>"
        f"<td style='text-align:right'>{int(r['emp'])}</td></tr>"
        for _,r in anual.sort_values(["empresa","año"]).iterrows()])

    total_group = g.groupby("empresa")["ventas_cop"].sum()
    grand_total = total_group.sum()
    rows_share = "".join([f"<tr><td>{emp}</td><td style='text-align:right'>{cop(v,1)}</td><td style='text-align:right'>{v/grand_total*100:.1f}%</td></tr>" for emp,v in total_group.items()])

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Reporte Consolidado del Grupo — CIMPA</title>{STYLE}</head><body>
    <div class="rpt-page">
      <div class="print-note">💡 Para guardar como PDF: <strong>Ctrl+P → Guardar como PDF</strong></div>
      {HEADER_HTML}
      <div class="rpt-title">🏢 Reporte Consolidado del Grupo Empresarial — {HOY_STR}</div>
      <div class="kpi-grid">
        {kpi_box("Empresas del grupo", "3", "CIMPA · Confía Control · Vasanico", True)}
        {kpi_box("Ventas consolidadas", cop(grand_total,1), "Período analizado", True)}
        {kpi_box("EBITDA consolidado", cop(g['ebitda_cop'].sum(),1), pct(g['ebitda_cop'].sum()/grand_total*100), g['ebitda_cop'].sum()/grand_total>0.12)}
        {kpi_box("Empleados grupo", str(g[g['periodo']==g['periodo'].max()]['n_empleados'].sum()), "Total nómina", True)}
        {kpi_box("Margen bruto grupo", pct(g['margen_bruto_cop'].sum()/grand_total*100), "Meta: 30%", g['margen_bruto_cop'].sum()/grand_total>0.30)}
        {kpi_box("Cartera grupo", cop(g.groupby('empresa')['cartera_cop'].last().sum(),1), "Último mes", True)}
      </div>
      <div class="section-title">Participación en ingresos por empresa</div>
      <table><thead><tr><th>Empresa</th><th style="text-align:right">Ventas COP</th><th style="text-align:right">Part. %</th></tr></thead>
      <tbody>{rows_share}</tbody></table>
      <div class="section-title">Comparativo anual por empresa</div>
      <table><thead><tr><th>Empresa</th><th style="text-align:right">Año</th><th style="text-align:right">Ventas</th><th style="text-align:right">Margen %</th><th style="text-align:right">EBITDA %</th><th style="text-align:right">Cartera</th><th style="text-align:right">Empleados</th></tr></thead>
      <tbody>{rows_anual}</tbody></table>
      {FOOTER_HTML}
    </div></body></html>"""


def build_logistica(d):
    ent = d[d["estado"]=="Entregado"]
    otd = (ent["entregado_a_tiempo"]==True).sum()/len(ent)*100 if len(ent) else 0
    dias_prom = ent["dias_transito"].mean() if len(ent) else 0
    retrasados = d[(d["estado"]=="En tránsito") & (d["fecha_entrega_prometida"] < pd.Timestamp(HOY))].shape[0]

    sede_otd = ent.groupby("sede_origen").agg(total=("despacho_id","count"), a_tiempo=("entregado_a_tiempo","sum")).reset_index()
    sede_otd["otd_pct"] = sede_otd["a_tiempo"]/sede_otd["total"]*100
    rows_sede = "".join([
        f"<tr><td>{r['sede_origen']}</td><td style='text-align:right'>{int(r['total'])}</td>"
        f"<td style='text-align:right'>{int(r['a_tiempo'])}</td>"
        f"<td style='text-align:right;font-weight:700;color:{'#22c55e' if r['otd_pct']>=85 else '#ef4444'}'>{r['otd_pct']:.1f}%</td></tr>"
        for _,r in sede_otd.sort_values("otd_pct",ascending=False).iterrows()])

    ret_det = d[(d["estado"]=="En tránsito") & (d["fecha_entrega_prometida"] < pd.Timestamp(HOY))].head(10)
    rows_ret = "".join([
        f"<tr><td>{r['despacho_id']}</td><td>{r['cliente']}</td>"
        f"<td>{r['sede_origen']} → {r['ciudad_destino']}</td>"
        f"<td>{r['fecha_pedido'].strftime('%Y-%m-%d')}</td>"
        f"<td>{r['fecha_entrega_prometida'].strftime('%Y-%m-%d')}</td>"
        f"<td>{tag('Retrasado','red')}</td></tr>"
        for _,r in ret_det.iterrows()])

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Reporte Logística — CIMPA</title>{STYLE}</head><body>
    <div class="rpt-page">
      <div class="print-note">💡 Para guardar como PDF: <strong>Ctrl+P → Guardar como PDF</strong></div>
      {HEADER_HTML}
      <div class="rpt-title">🚚 Reporte de Logística y Despachos — {HOY_STR}</div>
      <div class="kpi-grid">
        {kpi_box("Total despachos", str(len(d)), "Histórico", True)}
        {kpi_box("OTD global", pct(otd), "Meta: 85%", otd>=85)}
        {kpi_box("Días tránsito prom.", f"{dias_prom:.1f} días", "", dias_prom<3)}
        {kpi_box("En tránsito", str((d['estado']=='En tránsito').sum()), "", True)}
        {kpi_box("Retrasados", str(retrasados), "Vencida fecha prometida", retrasados==0)}
        {kpi_box("Valor total despachado", cop(d['valor_cop'].sum(),1), "", True)}
      </div>
      <div class="section-title">OTD por sede de origen</div>
      <table><thead><tr><th>Sede</th><th style="text-align:right">Total</th><th style="text-align:right">A tiempo</th><th style="text-align:right">OTD %</th></tr></thead>
      <tbody>{rows_sede}</tbody></table>
      <div class="section-title">Despachos retrasados ({retrasados})</div>
      {"<table><thead><tr><th>ID</th><th>Cliente</th><th>Ruta</th><th>F. Pedido</th><th>F. Prometida</th><th>Estado</th></tr></thead><tbody>" + rows_ret + "</tbody></table>" if retrasados > 0 else '<p style="color:#22c55e;font-weight:600">✅ No hay despachos retrasados en este momento.</p>'}
      {FOOTER_HTML}
    </div></body></html>"""


# ── MODULE RENDER ─────────────────────────────────────────────────────────────

def render():
    v, c, inv, d, emp, g = load()
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">C</div>
      <div>
        <div class="cb-title">Reportes Automáticos</div>
        <div class="cb-sub">Templates listos para descargar · Imprimir → Guardar como PDF</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{SURF};border:1px solid {BORDER};border-radius:12px;padding:16px 20px;margin-bottom:20px">
      <p style="font-size:13px;font-weight:600;color:{TEXT};margin:0 0 8px">📄 Cómo descargar como PDF</p>
      <p style="font-size:12px;color:{MUTED};margin:0;line-height:1.7">
        1. Haz clic en <strong style="color:{TEAL}">Descargar reporte</strong> para obtener el archivo HTML.<br>
        2. Abre el archivo descargado en tu navegador.<br>
        3. Presiona <strong>Ctrl+P</strong> (Windows) o <strong>Cmd+P</strong> (Mac).<br>
        4. En "Destino", selecciona <strong>"Guardar como PDF"</strong> y haz clic en Guardar.
      </p>
    </div>""", unsafe_allow_html=True)

    TEMPLATES = {
        "📊 Reporte Ejecutivo Mensual":   "Resumen general: ventas, cartera, inventario, OTD y grupo. Ideal para dirección.",
        "💰 Reporte de Ventas y Clientes":"Análisis por sede, categoría y cliente con top 10 productos.",
        "📋 Reporte de Cartera Vencida":  "Aging completo, alertas de mora y detalle de facturas vencidas.",
        "📦 Reporte de Inventario Crítico":"Stock crítico y bajo por sede, proveedor y cobertura.",
        "🚚 Reporte de Logística":        "OTD por sede, despachos retrasados y análisis de tránsito.",
        "🏢 Reporte Consolidado del Grupo":"CIMPA + Confía Control + Vasanico — comparativo anual.",
    }

    for i, (nombre, desc) in enumerate(TEMPLATES.items()):
        with st.expander(nombre, expanded=(i==0)):
            col_info, col_btn = st.columns([3,1])
            with col_info:
                st.markdown(f"<p style='color:{MUTED};font-size:13px;margin:4px 0 12px'>{desc}</p>", unsafe_allow_html=True)

            if "Ventas" in nombre:
                c1,c2 = st.columns(2)
                with c1:
                    sedes = ["Todas"] + sorted(v["sede_id"].unique().tolist())
                    sede_sel = st.selectbox("Sede", sedes, key=f"rpt_sede_{i}")
                with c2:
                    cats = ["Todas"] + sorted(v["categoria"].unique().tolist())
                    cat_sel = st.selectbox("Categoría", cats, key=f"rpt_cat_{i}")
            else:
                sede_sel = "Todas"; cat_sel = "Todas"

            if "Ejecutivo" in nombre:
                html = build_ejecutivo(v, c, inv, d, g)
                fname = "cimpa_reporte_ejecutivo.html"
            elif "Ventas" in nombre:
                html = build_ventas(v, sede_sel, cat_sel)
                fname = "cimpa_reporte_ventas.html"
            elif "Cartera" in nombre:
                html = build_cartera(c)
                fname = "cimpa_reporte_cartera.html"
            elif "Inventario" in nombre:
                html = build_inventario(inv)
                fname = "cimpa_reporte_inventario.html"
            elif "Logística" in nombre:
                html = build_logistica(d)
                fname = "cimpa_reporte_logistica.html"
            else:
                html = build_grupo(g)
                fname = "cimpa_reporte_grupo.html"

            # Preview KPIs inline
            st.markdown(_preview(nombre, v, c, inv, d, g), unsafe_allow_html=True)

            with col_btn:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                st.download_button(
                    label="⬇️ Descargar reporte",
                    data=html.encode("utf-8"),
                    file_name=fname,
                    mime="text/html",
                    key=f"dl_{i}",
                    use_container_width=True,
                )


def _preview(nombre, v, c, inv, d, g):
    v26 = v[v["fecha"].dt.year==2026]
    if "Ejecutivo" in nombre or "Ventas" in nombre:
        total = v26["total_cop"].sum()
        mg = v26["margen_pct"].mean()*100
        cli = v26["cliente_id"].nunique()
        items = [("Ventas 2026 YTD", cop(total,1)), ("Margen", pct(mg)), ("Clientes activos", str(cli))]
    elif "Cartera" in nombre:
        tot = c["valor_cop"].sum(); venc = c[c["dias_mora"]>0]["valor_cop"].sum()
        items = [("Total", cop(tot,1)), ("Vencida", cop(venc,1)), ("% vencida", pct(venc/tot*100))]
    elif "Inventario" in nombre:
        crit = (inv["estado"]=="Crítico").sum(); bajo = (inv["estado"]=="Bajo").sum()
        items = [("Valor total", cop(inv["valor_inventario"].sum(),1)), ("Críticos", str(crit)), ("Bajos", str(bajo))]
    elif "Logística" in nombre:
        ent = d[d["estado"]=="Entregado"]
        otd = (ent["entregado_a_tiempo"]==True).sum()/len(ent)*100 if len(ent) else 0
        ret = d[(d["estado"]=="En tránsito") & (d["fecha_entrega_prometida"] < pd.Timestamp(HOY))].shape[0]
        items = [("OTD", pct(otd)), ("En tránsito", str((d["estado"]=="En tránsito").sum())), ("Retrasados", str(ret))]
    else:
        grand = g["ventas_cop"].sum()
        items = [("Ventas grupo", cop(grand,1)), ("EBITDA", pct(g["ebitda_cop"].sum()/grand*100)), ("Empresas", "3")]

    boxes = "".join([f'<div style="background:{SURF2};border:1px solid {BORDER};border-radius:8px;padding:10px 14px;flex:1">'
                     f'<div style="font-size:10px;color:{MUTED};text-transform:uppercase;letter-spacing:.06em">{lab}</div>'
                     f'<div style="font-size:18px;font-weight:800;color:{TEXT};margin-top:4px">{val}</div></div>'
                     for lab,val in items])
    return f'<div style="display:flex;gap:10px;margin:8px 0 4px">{boxes}</div>'
