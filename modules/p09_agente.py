import streamlit as st
import pandas as pd
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

CONTEXTO_CIMPA = """
Eres el Agente de Inteligencia de CIMPA S.A.S., empresa colombiana con 30 años de experiencia distribuyendo
más de 2.000 insumos, aditivos, químicos, ingredientes y materias primas para la industria.

Datos clave de la empresa:
- 110 empleados · 6 sucursales + 2 CEDIs (Bogotá Américas, Bogotá Químicos, Itagüí, Villavicencio, Tunja, CEDI Mosquera, CEDI Siberia)
- Grupo: CIMPA (ingredientes alimentarios), Confía Control (análisis microbiológico y fisicoquímico), Vasanico (sabores e innovación)
- Distribuidor oficial de Vikan · Marcas propias: Choozit®, Yomix®, Cremodan®, Nisaplin®, Grindsted®, Refisal®

Categorías: Lácteos, Cárnicos, Panadería, Sabores & Colorantes, Aseo & Desinfección, Laboratorio.
Clientes clave: Alquería, Colanta, Alpina, Zenú, Bimbo, Noel, Postobón, Bavaria, Frupulpas, entre otros.
Proveedores: BASF, DSM/Danisco, Kerry Group, Brenntag, Univar, Givaudan, IFF, Merck, CP Kelco, Lesaffre, Chr. Hansen, Ingredion, Ecolab, PeroxyChem.
Responde siempre en español, de manera directa y profesional.
"""

def build_context() -> str:
    try:
        v   = pd.read_csv(DATA/"ventas.csv")
        v["fecha"] = pd.to_datetime(v["fecha"])
        c   = pd.read_csv(DATA/"cartera.csv")
        inv = pd.read_csv(DATA/"inventario.csv")
        d   = pd.read_csv(DATA/"despachos.csv")
        emp = pd.read_csv(DATA/"empleados.csv")
        g   = pd.read_csv(DATA/"grupo_mensual.csv")
        g["periodo"] = pd.to_datetime(g["periodo"])

        ref = pd.Timestamp("2026-08-22")
        v26 = v[v["fecha"].dt.year == 2026]
        vencida = c[c["dias_mora"]>0]["valor_cop"].sum()
        criticos = inv[inv["estado"]=="Crítico"].shape[0]
        bajos    = inv[inv["estado"]=="Bajo"].shape[0]
        entregados = d[d["estado"]=="Entregado"]
        otd = (entregados["entregado_a_tiempo"]==True).sum()/len(entregados)*100 if len(entregados) else 0

        g_ult = g.sort_values("periodo").tail(3)
        grupo_ventas = g_ult.groupby("empresa")["ventas_cop"].sum()

        resumen = f"""
=== RESUMEN OPERATIVO CIMPA (al 22 ago 2026) ===
VENTAS 2026 YTD: ${v26['total_cop'].sum()/1e9:.2f}B COP
  - Top cliente: {v26.groupby('cliente')['total_cop'].sum().idxmax()} (${v26.groupby('cliente')['total_cop'].sum().max()/1e6:.1f}M)
  - Mejor categoría: {v26.groupby('categoria')['total_cop'].sum().idxmax()}
  - Mejor sede: {v26.groupby('sede_id')['total_cop'].sum().idxmax()}

CARTERA:
  - Total: ${c['valor_cop'].sum()/1e9:.2f}B COP
  - Vencida: ${vencida/1e6:.1f}M ({vencida/c['valor_cop'].sum()*100:.1f}%)
  - Clientes en mora: {c[c['dias_mora']>0]['cliente'].nunique()}

INVENTARIO:
  - Valor total: ${inv['valor_inventario'].sum()/1e9:.2f}B COP
  - SKUs críticos: {criticos} | SKUs bajos: {bajos}
  - Cobertura promedio: {inv['dias_cobertura'].mean():.0f} días

LOGÍSTICA:
  - OTD (On-Time Delivery): {otd:.1f}%
  - En tránsito: {(d['estado']=='En tránsito').sum()} despachos

TALENTO:
  - Total empleados: {len(emp)}
  - Score desempeño prom: {emp['score_desempeno'].mean():.1f}/10
  - Ausentismo prom: {emp['dias_ausentismo'].mean():.1f} días/año

GRUPO (últimos 3 meses):
{chr(10).join([f'  - {emp_}: ${sal/1e9:.2f}B COP' for emp_, sal in grupo_ventas.items()])}
"""
        return resumen
    except Exception as ex:
        return f"[No se pudieron cargar datos: {ex}]"

SUGERIDAS = [
    "¿Cuáles son las ventas YTD?",
    "¿Qué clientes están en mora?",
    "¿Qué productos tienen stock crítico?",
    "¿Cuál es el margen por categoría?",
    "¿Cómo está el OTD de despachos?",
    "¿Qué sede vende más?",
    "¿Cuántos empleados tiene el grupo?",
    "Compara las 3 empresas del grupo",
]

def _procesar(pregunta: str, usar_demo: bool, api_key: str):
    st.session_state.ag_messages.append({"role": "user", "content": pregunta})
    if usar_demo:
        resp = generar_respuesta_demo(pregunta)
    elif api_key and api_key.startswith("sk-"):
        resp = llamar_claude(api_key, pregunta, build_context())
    else:
        resp = "Activa el Modo demo o ingresa un API key de Anthropic para recibir respuestas."
    st.session_state.ag_messages.append({"role": "assistant", "content": resp})

def render():
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">C</div>
      <div>
        <div class="cb-title">Agente IA CIMPA</div>
        <div class="cb-sub">Asistente inteligente · Consultas en lenguaje natural · Powered by Claude</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    if "ag_messages" not in st.session_state:
        st.session_state.ag_messages = []
    if "ag_pending" not in st.session_state:
        st.session_state.ag_pending = None

    # API key / modo
    col_a, col_b = st.columns([3, 1])
    with col_a:
        api_key = st.text_input("API Key de Anthropic", type="password",
            placeholder="sk-ant-...", key="ag_api",
            help="Ingresa tu API key de Anthropic para activar el agente con IA real")
    with col_b:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        usar_demo = st.toggle("Modo demo", value=True, key="ag_demo")

    # Sugeridas — botones reales
    st.markdown(f"<p style='font-size:13px;font-weight:700;color:{TEXT};margin:12px 0 8px'>💡 Preguntas sugeridas</p>", unsafe_allow_html=True)
    cols = st.columns(4)
    for idx, q in enumerate(SUGERIDAS):
        if cols[idx % 4].button(q, key=f"sug_{idx}", use_container_width=True):
            st.session_state.ag_pending = q

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Procesar pregunta pendiente (de botón sugerido)
    if st.session_state.ag_pending:
        _procesar(st.session_state.ag_pending, usar_demo, api_key)
        st.session_state.ag_pending = None

    # Historial
    for msg in st.session_state.ag_messages:
        role_color = PURPLE if msg["role"] == "user" else TEAL
        role_label = "Tú" if msg["role"] == "user" else "🤖 Agente CIMPA"
        st.markdown(f"""
        <div style="background:{SURF};border:1px solid {BORDER};border-radius:10px;
          padding:14px 18px;margin:6px 0;border-left:3px solid {role_color}">
          <p style="font-size:11px;font-weight:700;color:{role_color};margin:0 0 8px;
            text-transform:uppercase;letter-spacing:.08em">{role_label}</p>
          <p style="color:{TEXT};margin:0;line-height:1.65;white-space:pre-wrap">{msg['content']}</p>
        </div>""", unsafe_allow_html=True)

    # Chat input libre
    pregunta = st.chat_input("Escribe cualquier pregunta sobre el negocio de CIMPA...")
    if pregunta:
        _procesar(pregunta, usar_demo, api_key)
        st.rerun()

    if st.button("🗑️ Limpiar conversación", key="ag_clear"):
        st.session_state.ag_messages = []
        st.rerun()


def generar_respuesta_demo(pregunta: str) -> str:
    p = pregunta.lower()
    try:
        v   = pd.read_csv(DATA/"ventas.csv")
        v["fecha"] = pd.to_datetime(v["fecha"])
        c   = pd.read_csv(DATA/"cartera.csv")
        inv = pd.read_csv(DATA/"inventario.csv")
        d   = pd.read_csv(DATA/"despachos.csv")
        emp = pd.read_csv(DATA/"empleados.csv")
        v26 = v[v["fecha"].dt.year==2026]
    except Exception as ex:
        return f"Error cargando datos: {ex}"

    if any(x in p for x in ["venta","ingreso","ytd","facturación"]):
        total = v26["total_cop"].sum()
        top_c = v26.groupby("cliente")["total_cop"].sum().idxmax()
        top_s = v26.groupby("sede_id")["total_cop"].sum().idxmax()
        top_k = v26.groupby("categoria")["total_cop"].sum().idxmax()
        return (f"📊 Ventas acumuladas 2026 (YTD): ${total/1e9:.2f}B COP\n\n"
                f"• Top cliente: {top_c} (${v26.groupby('cliente')['total_cop'].sum().max()/1e6:.0f}M)\n"
                f"• Mejor categoría: {top_k}\n"
                f"• Sede líder: {top_s}\n"
                f"• Ticket promedio: ${v26['total_cop'].mean()/1e3:.0f}K COP\n\n"
                f"En lo que va del año, CIMPA muestra un crecimiento saludable liderado por {top_k}.")

    elif any(x in p for x in ["mora","cartera","cobro","vencid"]):
        venc = c[c["dias_mora"]>0]
        total_venc = venc["valor_cop"].sum()
        n_cli = venc["cliente"].nunique()
        peor  = venc.groupby("cliente")["valor_cop"].sum().nlargest(3)
        txt_peor = "\n".join([f"  • {cli}: ${v/1e6:.1f}M" for cli, v in peor.items()])
        return (f"📋 Cartera vencida: ${total_venc/1e6:.1f}M COP ({total_venc/c['valor_cop'].sum()*100:.1f}% del total)\n\n"
                f"• {n_cli} clientes con facturas vencidas\n"
                f"• Días de mora promedio: {venc['dias_mora'].mean():.0f} días\n"
                f"• Cartera +90 días: ${c[c['dias_mora']>90]['valor_cop'].sum()/1e6:.1f}M\n\n"
                f"Top 3 clientes con mayor deuda vencida:\n{txt_peor}")

    elif any(x in p for x in ["stock","inventario","crítico","bodega","escasez"]):
        crit = inv[inv["estado"]=="Crítico"]
        bajo = inv[inv["estado"]=="Bajo"]
        return (f"📦 Estado del inventario:\n\n"
                f"• Valor total: ${inv['valor_inventario'].sum()/1e9:.2f}B COP\n"
                f"• SKUs críticos (bajo mínimo): {len(crit)}\n"
                f"• SKUs en nivel bajo: {len(bajo)}\n"
                f"• Cobertura promedio: {inv['dias_cobertura'].mean():.0f} días\n\n"
                f"Productos críticos:\n" +
                "\n".join([f"  • {r['producto']} ({r['sede_nombre']}): stock {r['stock_actual']} / mín {r['stock_minimo']}"
                            for _, r in crit.head(5).iterrows()]))

    elif any(x in p for x in ["despacho","entrega","otd","logística","transporte"]):
        ent = d[d["estado"]=="Entregado"]
        otd = (ent["entregado_a_tiempo"]==True).sum()/len(ent)*100 if len(ent) else 0
        ret = d[(d["estado"]=="En tránsito")].shape[0]
        return (f"🚚 Logística y despachos:\n\n"
                f"• OTD (On-Time Delivery): {otd:.1f}%\n"
                f"• Total despachos: {len(d)}\n"
                f"• En tránsito: {ret}\n"
                f"• Días de tránsito promedio: {ent['dias_transito'].mean():.1f} días\n\n"
                f"{'✅ La operación logística está cumpliendo la meta del 85%.' if otd>=85 else '⚠️ El OTD está por debajo de la meta del 85%. Se recomienda revisar las rutas con mayor retraso.'}")

    elif any(x in p for x in ["empleado","talento","rrhh","personal","salario","nómina"]):
        return (f"👥 Talento Humano:\n\n"
                f"• Total empleados: {len(emp)}\n"
                f"• Masa salarial mensual: ${emp['salario_cop'].sum()/1e6:.1f}M COP\n"
                f"• Salario promedio: ${emp['salario_cop'].mean()/1e6:.2f}M COP\n"
                f"• Score desempeño promedio: {emp['score_desempeno'].mean():.1f}/10\n"
                f"• Ausentismo promedio: {emp['dias_ausentismo'].mean():.1f} días/año\n\n"
                f"Sede con mayor personal: {emp.groupby('sede').size().idxmax()} "
                f"({emp.groupby('sede').size().max()} empleados)")

    elif any(x in p for x in ["grupo","cimpa","confía","vasanico","empresa","consolidado"]):
        return ("🏢 El Grupo cuenta con 3 empresas:\n\n"
                "• CIMPA: Distribuidor de ingredientes alimentarios. Sede principal en Bogotá. Mayor volumen del grupo.\n"
                "• Confía Control: Especialista en higiene industrial y control de plagas. Opera con química especializada.\n"
                "• Vasanico: Enfocada en reactivos y materiales de laboratorio.\n\n"
                "En conjunto, el grupo maneja 7 bodegas, 110+ empleados y atiende a más de 20 grandes clientes industriales.")

    elif any(x in p for x in ["margen","rentabilidad","ganancia","utilidad"]):
        mg = v26.groupby("categoria")["margen_pct"].mean().sort_values(ascending=False) * 100
        lines = "\n".join([f"  • {cat}: {m:.1f}%" for cat, m in mg.items()])
        return (f"📊 Margen bruto promedio 2026:\n\n"
                f"• General: {v26['margen_pct'].mean()*100:.1f}%\n\n"
                f"Por categoría:\n{lines}\n\n"
                f"{'✅ El margen supera la meta del 30%.' if v26['margen_pct'].mean()*100>=30 else '⚠️ El margen está por debajo de la meta del 30%.'}")

    else:
        total26 = v26["total_cop"].sum()
        top_cat = v26.groupby("categoria")["total_cop"].sum().idxmax()
        top_cli = v26.groupby("cliente")["total_cop"].sum().idxmax()
        crit    = (inv["estado"]=="Crítico").sum()
        ent     = d[d["estado"]=="Entregado"]
        otd     = (ent["entregado_a_tiempo"]==True).sum()/len(ent)*100 if len(ent) else 0
        return (f"Entendido. Aquí un resumen rápido del negocio para orientarte:\n\n"
                f"📊 Ventas 2026 YTD: {cop(total26,1)} COP · Categoría líder: {top_cat} · Top cliente: {top_cli}\n"
                f"📋 Cartera vencida: {cop(c[c['dias_mora']>0]['valor_cop'].sum(),1)} · {c[c['dias_mora']>0]['cliente'].nunique()} clientes en mora\n"
                f"📦 Stock: {crit} SKUs en estado crítico · Cobertura prom. {inv['dias_cobertura'].mean():.0f} días\n"
                f"🚚 OTD: {otd:.1f}% · {(d['estado']=='En tránsito').sum()} despachos en ruta\n\n"
                f"Puedo profundizar en cualquier tema. Usa las preguntas sugeridas arriba o escríbeme directamente.\n"
                f"Temas disponibles: ventas, cartera, inventario, despachos, talento, grupo empresarial, márgenes.")


def llamar_claude(api_key: str, pregunta: str, contexto: str) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        historial = [{"role": m["role"], "content": m["content"]}
                     for m in st.session_state.ag_messages[:-1]]
        historial.append({"role": "user", "content": pregunta})
        response = client.messages.create(
            model="claude-opus-5",
            max_tokens=1024,
            system=CONTEXTO_CIMPA + "\n\n" + contexto,
            messages=historial
        )
        return response.content[0].text
    except Exception as ex:
        return f"Error al conectar con Claude: {ex}"
