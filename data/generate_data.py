"""
CIMPA — Generador de datos demo
Corre una vez: python data/generate_data.py
Genera todos los CSVs en esta misma carpeta.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

RNG = np.random.default_rng(42)
OUT = Path(__file__).parent

# ── MASTERS ──────────────────────────────────────────────────────────────────

SEDES = [
    {"sede_id": "BOG-AME", "nombre": "Bogotá · Américas",  "ciudad": "Bogotá",        "depto": "Cundinamarca", "tipo": "Punto de Venta", "peso": 0.34},
    {"sede_id": "BOG-QUI", "nombre": "Bogotá · Químicos",   "ciudad": "Bogotá",        "depto": "Cundinamarca", "tipo": "Punto de Venta", "peso": 0.14},
    {"sede_id": "ITA",     "nombre": "Itagüí",              "ciudad": "Itagüí",        "depto": "Antioquia",    "tipo": "Punto de Venta", "peso": 0.21},
    {"sede_id": "VIL",     "nombre": "Villavicencio",       "ciudad": "Villavicencio", "depto": "Meta",         "tipo": "Punto de Venta", "peso": 0.09},
    {"sede_id": "TUN",     "nombre": "Tunja",               "ciudad": "Tunja",         "depto": "Boyacá",       "tipo": "Punto de Venta", "peso": 0.07},
    {"sede_id": "MOS",     "nombre": "CEDI Mosquera",       "ciudad": "Mosquera",      "depto": "Cundinamarca", "tipo": "CEDI",           "peso": 0.10},
    {"sede_id": "SIB",     "nombre": "CEDI Siberia",        "ciudad": "Siberia",       "depto": "Cundinamarca", "tipo": "CEDI",           "peso": 0.05},
]

PRODUCTOS = [
    # ── Lácteos — cultivos, coagulantes y estabilizantes reales de CIMPA
    ("LAC-001","Cuajo Chymostar® líquido",     "Lácteos","litro","Chr. Hansen",95000,142000,40,30),
    ("LAC-002","Cuajo Marschall® pastilla",     "Lácteos","sobre","Chr. Hansen",12000,18500,200,30),
    ("LAC-003","Choozit® MA 4001",              "Lácteos","dosis","Danisco",185000,275000,20,50),
    ("LAC-004","Choozit® MM 100",               "Lácteos","dosis","Danisco",175000,260000,20,50),
    ("LAC-005","Yomix® 883 (yogurt)",           "Lácteos","dosis","Danisco",165000,245000,25,50),
    ("LAC-006","Yomix® Prime 800",              "Lácteos","dosis","Danisco",172000,255000,25,50),
    ("LAC-007","Lactogel® FX 7720",             "Lácteos","kg","Danisco",88000,132000,60,45),
    ("LAC-008","Cremodan® SE 709-2",            "Lácteos","kg","Danisco",92000,138000,50,45),
    ("LAC-009","Nisaplin® (Nisin A)",           "Lácteos","kg","Danisco",380000,565000,8,60),
    ("LAC-010","Cloruro de calcio alimentario", "Lácteos","kg","Brenntag",8500,14200,200,7),
    # ── Cárnicos — fosfatos, proteínas y condimentos
    ("CAR-001","Tripolifosfato sódico STPP",    "Cárnicos","kg","BASF",12000,18500,300,30),
    ("CAR-002","Eritorbato de sodio",           "Cárnicos","kg","Brenntag",14500,22000,200,7),
    ("CAR-003","Carragenina Iota cárnicos",     "Cárnicos","kg","Kerry Group",41000,62000,80,45),
    ("CAR-004","Condimento chorizo especial",   "Cárnicos","kg","Givaudan",68000,102000,50,15),
    ("CAR-005","Condimento mortadela premium",  "Cárnicos","kg","IFF",72000,108000,50,15),
    ("CAR-006","Proteína de soya texturizada",  "Cárnicos","kg","Brenntag",9500,14500,400,7),
    ("CAR-007","Proteína aislada de soya 90%",  "Cárnicos","kg","Brenntag",22000,33000,150,7),
    ("CAR-008","Almidón de papa para cárnicos", "Cárnicos","kg","Ingredion",6500,10200,500,10),
    ("CAR-009","Sal Refisal® curación",         "Cárnicos","kg","Refisal",3200,5800,500,3),
    ("CAR-010","Nitrito de sodio 99%",          "Cárnicos","kg","Univar",18000,27000,150,40),
    # ── Panadería — mejoradores, levaduras y enzimas
    ("PAN-001","Levadura seca instantánea",     "Panadería","kg","Lesaffre",12500,19000,300,20),
    ("PAN-002","Mejorizador panadera CM-5",     "Panadería","kg","Kerry Group",19000,29000,150,35),
    ("PAN-003","Propionato de calcio",          "Panadería","kg","Univar",16500,25000,200,25),
    ("PAN-004","Ácido ascórbico E300",          "Panadería","kg","Brenntag",24000,36000,150,7),
    ("PAN-005","DATEM emulsificante pan",       "Panadería","kg","BASF",18000,27500,100,35),
    ("PAN-006","Enzima amilasa fungal",         "Panadería","kg","DSM",58000,88000,40,45),
    ("PAN-007","Enzima xilanasa panadera",      "Panadería","kg","DSM",72000,108000,25,45),
    ("PAN-008","Monoglicérido destilado",       "Panadería","kg","BASF",21000,32000,100,30),
    # ── Sabores & Colorantes (línea Vasanico)
    ("SAB-001","Sabor artificial vainilla",     "Sabores & Colorantes","kg","Vasanico",48000,75000,80,5),
    ("SAB-002","Sabor natural fresa premium",   "Sabores & Colorantes","kg","Vasanico",62000,95000,60,5),
    ("SAB-003","Sabor natural durazno",         "Sabores & Colorantes","kg","Vasanico",58000,88000,60,5),
    ("SAB-004","Colorante caramelo IV",         "Sabores & Colorantes","kg","Brenntag",18500,28000,100,7),
    ("SAB-005","Colorante curcumina natural",   "Sabores & Colorantes","kg","Chr. Hansen",95000,145000,20,30),
    ("SAB-006","Sucralosa",                     "Sabores & Colorantes","kg","Univar",125000,185000,20,40),
    ("SAB-007","Stevia RA97",                   "Sabores & Colorantes","kg","Ingredion",145000,215000,15,50),
    ("SAB-008","Ácido cítrico anhidro",         "Sabores & Colorantes","kg","Brenntag",7800,12500,500,7),
    ("SAB-009","Goma xantana",                  "Sabores & Colorantes","kg","CP Kelco",42000,63000,80,40),
    ("SAB-010","Pectina HM cítrica",            "Sabores & Colorantes","kg","CP Kelco",55000,82000,50,40),
    # ── Aseo & Desinfección — línea VIKAN + insumos
    ("ASE-001","Hipoclorito de sodio 15%",      "Aseo & Desinfección","litro","Coyabra",2800,4800,1000,3),
    ("ASE-002","Alcohol etílico 96°",           "Aseo & Desinfección","litro","Coyabra",6500,10500,500,3),
    ("ASE-003","Detergente alcalino CIP-100",   "Aseo & Desinfección","kg","Ecolab",18000,27000,200,7),
    ("ASE-004","Ácido peracético 15%",          "Aseo & Desinfección","litro","PeroxyChem",28000,42000,80,30),
    ("ASE-005","Amonio cuaternario QAT-50",     "Aseo & Desinfección","litro","Univar",22000,33000,100,20),
    ("ASE-006","Cepillo VIKAN higiene azul",    "Aseo & Desinfección","unidad","Vikan",38000,58000,30,15),
    # ── Laboratorio — medios de cultivo Merck + equipos
    ("LAB-001","Agar PCA recuento total",       "Laboratorio","500g","Merck",185000,275000,10,45),
    ("LAB-002","Agar VRBD coliformes",          "Laboratorio","500g","Merck",195000,290000,8,45),
    ("LAB-003","Agar Baird-Parker S. aureus",   "Laboratorio","500g","Merck",220000,325000,8,45),
    ("LAB-004","Agar Salmonella-Shigella",      "Laboratorio","500g","Merck",205000,305000,8,45),
    ("LAB-005","Kit coloración Gram",           "Laboratorio","kit","Merck",85000,128000,20,30),
    ("LAB-006","Prueba rápida coliformes",      "Laboratorio","caja","Confía Control",75000,118000,15,5),
]
PROD_COLS = ["producto_id","nombre","categoria","unidad","proveedor_principal","precio_costo","precio_venta","stock_min","lead_time_dias"]

CLIENTES = [
    ("CLI-001","Alquería S.A.",            "Lácteos",            "Bogotá",        "Cundinamarca",60,800_000_000,"BOG-AME"),
    ("CLI-002","Colanta Ltda.",            "Lácteos",            "Medellín",      "Antioquia",   45,600_000_000,"ITA"),
    ("CLI-003","Alpina S.A.",              "Lácteos",            "Bogotá",        "Cundinamarca",60,700_000_000,"BOG-AME"),
    ("CLI-004","Gloria Colombia",          "Lácteos",            "Bogotá",        "Cundinamarca",60,400_000_000,"MOS"),
    ("CLI-005","Lácteos El Recreo",        "Lácteos",            "Tunja",         "Boyacá",      30,120_000_000,"TUN"),
    ("CLI-006","Procesadora Meta Lácteos", "Lácteos",            "Villavicencio", "Meta",        30,100_000_000,"VIL"),
    ("CLI-007","La Carreta Alimentos",     "Cárnicos",           "Bogotá",        "Cundinamarca",30,350_000_000,"BOG-AME"),
    ("CLI-008","Zenú S.A.S.",              "Cárnicos",           "Medellín",      "Antioquia",   45,500_000_000,"ITA"),
    ("CLI-009","Rica Rondo S.A.",          "Cárnicos",           "Bogotá",        "Cundinamarca",30,300_000_000,"BOG-QUI"),
    ("CLI-010","Frigorífico Guadalupe",    "Cárnicos",           "Bogotá",        "Cundinamarca",45,180_000_000,"MOS"),
    ("CLI-011","Frigoríficos El Progreso", "Cárnicos",           "Villavicencio", "Meta",        30,150_000_000,"VIL"),
    ("CLI-012","Bimbo Colombia",           "Panadería",          "Bogotá",        "Cundinamarca",30,400_000_000,"BOG-AME"),
    ("CLI-013","Noel S.A.S.",              "Panadería",          "Medellín",      "Antioquia",   45,350_000_000,"ITA"),
    ("CLI-014","Pan Pa' Ya",               "Panadería",          "Bogotá",        "Cundinamarca",30,200_000_000,"BOG-AME"),
    ("CLI-015","Postobón S.A.",            "Sabores & Colorantes","Bogotá",       "Cundinamarca",60,600_000_000,"SIB"),
    ("CLI-016","Bavaria S.A.",             "Sabores & Colorantes","Bogotá",       "Cundinamarca",45,450_000_000,"BOG-QUI"),
    ("CLI-017","Frupulpas S.A.S.",         "Sabores & Colorantes","Bogotá",       "Cundinamarca",30,250_000_000,"BOG-AME"),
    ("CLI-018","Laboratorios LABOFARMA",   "Laboratorio",        "Bogotá",        "Cundinamarca",30,150_000_000,"BOG-QUI"),
    ("CLI-019","Centro Análisis ALF",      "Laboratorio",        "Medellín",      "Antioquia",   30,120_000_000,"ITA"),
    ("CLI-020","Sodexo Colombia",          "Aseo & Desinfección","Bogotá",        "Cundinamarca",30,200_000_000,"MOS"),
    ("CLI-021","Hotel Las Américas",       "Aseo & Desinfección","Bogotá",        "Cundinamarca",30,100_000_000,"BOG-AME"),
    ("CLI-022","Avícola Los Llanos",       "Cárnicos",           "Villavicencio", "Meta",        30,130_000_000,"VIL"),
]
CLI_COLS = ["cliente_id","nombre","sector","ciudad","depto","credito_dias","cupo_credito_cop","sede_principal"]

PROVEEDORES = [
    ("PRO-001","BASF SE","Alemania","EUR",35,"Química industrial, emulsificantes, fosfatos",9.1,8.5,7.8),
    ("PRO-002","DSM Nutritional","Países Bajos","EUR",50,"Enzimas, vitaminas, cultivos, conservantes",9.4,8.8,7.2),
    ("PRO-003","Kerry Group","Irlanda","USD",45,"Ingredientes funcionales, carrageninas, mejorizadores",8.8,8.4,7.5),
    ("PRO-004","Brenntag Colombia","Colombia","COP",7,"Distribución de químicos, ácidos, conservantes",8.2,9.0,8.8),
    ("PRO-005","Univar Solutions","EEUU","USD",40,"Edulcorantes, nitratos, amonio cuaternario",8.0,8.2,8.0),
    ("PRO-006","Givaudan Colombia","Colombia","COP",15,"Condimentos y saborizantes cárnicos",9.2,9.1,7.4),
    ("PRO-007","IFF Colombia","Colombia","COP",15,"Saborizantes y fragancias",9.0,8.9,7.6),
    ("PRO-008","Merck KGaA","Alemania","EUR",45,"Medios de cultivo, reactivos laboratorio",9.5,8.6,7.0),
    ("PRO-009","CP Kelco","EEUU","USD",50,"Gomas xantana, pectinas",8.7,8.3,7.8),
    ("PRO-010","Lesaffre","Francia","EUR",20,"Levaduras y mejoradores panadería",8.6,8.8,8.2),
    ("PRO-011","Chr. Hansen","Dinamarca","EUR",30,"Cultivos lácteos, enzimas",9.3,9.0,7.3),
    ("PRO-012","Ingredion Colombia","Colombia","COP",10,"Almidones, stevia, ingredientes bebidas",8.4,8.7,8.5),
    ("PRO-013","Ecolab Colombia","Colombia","COP",10,"Detergentes y desinfectantes industriales",8.9,9.2,8.1),
    ("PRO-014","Coyabra","Colombia","COP",5,"Hipoclorito, alcohol, aseo básico",7.8,9.3,9.2),
    ("PRO-015","PeroxyChem","EEUU","USD",30,"Ácido peracético, desinfectantes oxidantes",8.5,8.4,7.9),
]
PRO_COLS = ["proveedor_id","proveedor","pais","moneda","lead_time_avg_dias","especialidad","score_calidad","score_puntualidad","score_precio"]


# ── HELPERS ───────────────────────────────────────────────────────────────────

def seasonal(month: int) -> float:
    m = {1:0.82,2:0.88,3:0.97,4:1.00,5:1.02,6:1.06,
         7:1.00,8:0.96,9:1.04,10:1.08,11:1.18,12:1.35}
    return m.get(month, 1.0)


# ── GENERATE ──────────────────────────────────────────────────────────────────

def gen_maestros():
    pd.DataFrame(PRODUCTOS, columns=PROD_COLS).to_csv(OUT/"productos.csv", index=False)
    pd.DataFrame(CLIENTES,  columns=CLI_COLS ).to_csv(OUT/"clientes.csv",  index=False)
    pr = pd.DataFrame(PROVEEDORES, columns=PRO_COLS)
    pr["score_general"] = ((pr["score_calidad"]*0.4 + pr["score_puntualidad"]*0.35 + pr["score_precio"]*0.25)).round(2)
    pr.to_csv(OUT/"proveedores.csv", index=False)
    pd.DataFrame(SEDES).to_csv(OUT/"sedes.csv", index=False)


def gen_ventas():
    prods = pd.DataFrame(PRODUCTOS, columns=PROD_COLS)
    clien = pd.DataFrame(CLIENTES,  columns=CLI_COLS)
    sedes = pd.DataFrame(SEDES)
    cat_sector = {
        "Lácteos":            ["Lácteos"],
        "Cárnicos":           ["Cárnicos"],
        "Panadería":          ["Panadería"],
        "Sabores & Colorantes":["Sabores & Colorantes","Lácteos","Panadería","Cárnicos"],
        "Aseo & Desinfección":["Aseo & Desinfección"],
        "Laboratorio":        ["Laboratorio"],
    }
    rows = []
    start = date(2025, 1, 1)
    end   = date(2026, 8, 22)
    d = start
    while d <= end:
        if d.weekday() < 6:
            base_orders = int(RNG.integers(18, 32))
            factor = seasonal(d.month) * (1 + 0.01 * ((d - start).days / 30))
            n_orders = max(5, int(base_orders * factor))
            for _ in range(n_orders):
                sede = RNG.choice(sedes["sede_id"].values, p=sedes["peso"].values)
                prod = prods.sample(1, random_state=int(RNG.integers(0,9999))).iloc[0]
                sectors = cat_sector.get(prod["categoria"], clien["sector"].unique().tolist())
                cand = clien[clien["sector"].isin(sectors)]
                if cand.empty: cand = clien
                cli = cand.sample(1, random_state=int(RNG.integers(0,9999))).iloc[0]
                qty = float(RNG.integers(10, 1200)) * 0.1
                precio = prod["precio_venta"] * RNG.uniform(0.92, 1.05)
                descuento = RNG.choice([0,0,0,0.02,0.03,0.05], p=[0.5,0.2,0.1,0.1,0.05,0.05])
                total = qty * precio * (1 - descuento)
                margen = (prod["precio_venta"] - prod["precio_costo"]) / prod["precio_venta"]
                rows.append({
                    "fecha": d.isoformat(), "mes": d.strftime("%Y-%m"),
                    "cliente_id": cli["cliente_id"], "cliente": cli["nombre"],
                    "sector_cliente": cli["sector"],
                    "producto_id": prod["producto_id"], "producto": prod["nombre"],
                    "categoria": prod["categoria"], "sede_id": sede,
                    "cantidad": round(qty, 2), "unidad": prod["unidad"],
                    "precio_unitario": round(precio),
                    "descuento_pct": descuento, "total_cop": round(total),
                    "margen_pct": round(margen, 3),
                })
        d += timedelta(days=1)
    pd.DataFrame(rows).to_csv(OUT/"ventas.csv", index=False)
    print(f"  ventas.csv → {len(rows):,} filas")


def gen_inventario():
    prods = pd.DataFrame(PRODUCTOS, columns=PROD_COLS)
    rows = []
    for _, sede in pd.DataFrame(SEDES).iterrows():
        for _, prod in prods.iterrows():
            mult = 3.0 if sede["tipo"] == "CEDI" else 1.0
            stock_max = prod["stock_min"] * RNG.uniform(4, 10) * mult
            stock_act = prod["stock_min"] * RNG.uniform(0.4, 6.0) * mult
            dias_cob = (stock_act / max(1, prod["stock_min"] / 30)) if prod["stock_min"] > 0 else 0
            rows.append({
                "sede_id": sede["sede_id"], "sede_nombre": sede["nombre"],
                "ciudad": sede["ciudad"], "producto_id": prod["producto_id"],
                "producto": prod["nombre"], "categoria": prod["categoria"],
                "unidad": prod["unidad"], "proveedor": prod["proveedor_principal"],
                "stock_actual": round(stock_act, 1),
                "stock_minimo": prod["stock_min"],
                "stock_maximo": round(stock_max, 1),
                "precio_costo": prod["precio_costo"],
                "valor_inventario": round(stock_act * prod["precio_costo"]),
                "dias_cobertura": round(min(dias_cob, 180), 1),
                "estado": ("Crítico" if stock_act < prod["stock_min"] * 0.5 else
                           "Bajo"    if stock_act < prod["stock_min"] else
                           "Normal"  if stock_act < prod["stock_min"] * 3 else "Alto"),
            })
    pd.DataFrame(rows).to_csv(OUT/"inventario.csv", index=False)
    print(f"  inventario.csv → {len(rows)} filas")


def gen_cartera():
    clien = pd.DataFrame(CLIENTES, columns=CLI_COLS)
    rows = []
    fac_id = 1000
    base = date(2026, 4, 1)
    for _, cli in clien.iterrows():
        n_facturas = int(RNG.integers(4, 14))
        for i in range(n_facturas):
            dias_emision = int(RNG.integers(1, 120))
            f_factura = base - timedelta(days=dias_emision)
            f_vencimiento = f_factura + timedelta(days=int(cli["credito_dias"]))
            dias_mora = max(0, (date(2026, 8, 22) - f_vencimiento).days)
            valor = float(RNG.integers(8_000_000, 180_000_000))
            estado = ("Vigente" if dias_mora == 0 else
                      "Vencida 1-30"  if dias_mora <= 30 else
                      "Vencida 31-60" if dias_mora <= 60 else
                      "Vencida 61-90" if dias_mora <= 90 else "Vencida +90")
            rows.append({
                "factura_id": f"FAC-{fac_id}",
                "cliente_id": cli["cliente_id"], "cliente": cli["nombre"],
                "sector": cli["sector"], "ciudad": cli["ciudad"],
                "credito_dias": cli["credito_dias"],
                "fecha_factura": f_factura.isoformat(),
                "fecha_vencimiento": f_vencimiento.isoformat(),
                "dias_mora": dias_mora, "valor_cop": round(valor), "estado": estado,
            })
            fac_id += 1
    pd.DataFrame(rows).to_csv(OUT/"cartera.csv", index=False)
    print(f"  cartera.csv → {len(rows)} filas")


def gen_empleados():
    depts = ["Comercial","Logística","Operaciones","Calidad","Administración","Talento Humano","Dirección"]
    cargos_map = {
        "Comercial":       ["Vendedor Jr.","Asesor Comercial","Key Account Manager","Director Comercial"],
        "Logística":       ["Auxiliar Bodega","Conductor","Coordinador Logístico","Jefe de Bodega"],
        "Operaciones":     ["Auxiliar Operativo","Técnico Operativo","Coordinador Operativo"],
        "Calidad":         ["Analista de Calidad","Bacteriólogo","Director Técnico"],
        "Administración":  ["Auxiliar Contable","Contador","Tesorero","Jefe Administrativo"],
        "Talento Humano":  ["Analista TH","Gerente TH Grupo"],
        "Dirección":       ["Director Nacional PV","Gerente General","Gerente Regional"],
    }
    contratos = ["Indefinido","Indefinido","Indefinido","Fijo","Obra labor","Pasantía"]
    sedes_df = pd.DataFrame(SEDES)
    sedes_list = sedes_df["sede_id"].values
    sede_nombres = dict(zip(sedes_df["sede_id"], sedes_df["nombre"]))
    sede_pesos = sedes_df["peso"].values
    nombres_m = ["Andrés","Carlos","Juan","Diego","Luis","Mauricio","Omar","Oscar","Camilo","Jorge"]
    nombres_f = ["María","Daniela","Laura","Juliana","Paola","Andrea","Valentina","Natalia","Mónica","Sandra"]
    apellidos = ["García","Martínez","López","Rodríguez","González","Hernández","Vargas","Castro","Morales","Pérez",
                 "Rojas","Díaz","Torres","Ramírez","Sánchez","Reyes","Gómez","Muñoz","Jiménez","Barreto"]
    rows = []
    for i in range(110):
        dept = RNG.choice(depts)
        cargo = str(RNG.choice(cargos_map[dept]))
        genero = str(RNG.choice(["M","F"]))
        nombre = str(RNG.choice(nombres_m if genero == "M" else nombres_f))
        apellido = f"{RNG.choice(apellidos)} {RNG.choice(apellidos)}"
        sede_id = str(RNG.choice(sedes_list, p=sede_pesos))
        ingreso = date(2026, 8, 22) - timedelta(days=int(RNG.integers(30, 3650)))
        antiguedad = round((date(2026, 8, 22) - ingreso).days / 365, 1)
        edad = int(RNG.integers(22, 58))
        salario = int({
            "Dirección":      RNG.integers(8_000_000, 18_000_000),
            "Comercial":      RNG.integers(2_800_000,  7_000_000),
            "Calidad":        RNG.integers(3_200_000,  6_500_000),
            "Administración": RNG.integers(2_500_000,  5_500_000),
            "Logística":      RNG.integers(1_900_000,  3_800_000),
            "Operaciones":    RNG.integers(1_900_000,  3_500_000),
            "Talento Humano": RNG.integers(3_500_000,  8_000_000),
        }[dept])
        rows.append({
            "empleado_id":   f"EMP-{i+1:03d}",
            "nombre":        f"{nombre} {apellido}",
            "genero":        genero,
            "edad":          edad,
            "departamento":  dept,
            "cargo":         cargo,
            "tipo_contrato": str(RNG.choice(contratos)),
            "sede":          sede_nombres[sede_id],
            "sede_id":       sede_id,
            "fecha_ingreso": ingreso.isoformat(),
            "antiguedad_anos": antiguedad,
            "salario_cop":   salario,
            "score_desempeno": round(float(RNG.uniform(5.5, 10.0)), 1),
            "dias_ausentismo": int(RNG.integers(0, 18)),
            "estado":        "Activo" if RNG.random() > 0.04 else "Inactivo",
        })
    pd.DataFrame(rows).to_csv(OUT/"empleados.csv", index=False)
    print(f"  empleados.csv → {len(rows)} filas")


def gen_ordenes_compra():
    prods = pd.DataFrame(PRODUCTOS, columns=PROD_COLS)
    pros  = pd.DataFrame(PROVEEDORES, columns=PRO_COLS)
    rows = []
    oc_id = 500
    today = date(2026, 8, 22)
    for _ in range(68):
        dias_atras = int(RNG.integers(3, 90))
        f_orden = today - timedelta(days=dias_atras)
        prov = pros.sample(1, random_state=int(RNG.integers(0,9999))).iloc[0]
        lt = int(prov["lead_time_avg_dias"] * RNG.uniform(0.8, 1.3))
        f_esperada = f_orden + timedelta(days=lt)
        recibida = f_esperada < today
        delay = int(RNG.integers(0, 8)) if recibida else 0
        f_real = f_esperada + timedelta(days=delay) if recibida else None
        estado = "Recibida" if recibida else RNG.choice(["En tránsito","En tránsito","Confirmada","En aduana"])
        # Pick a few productos for this OC and derive category
        prod_sel = prods.sample(n=int(RNG.integers(1, 5)), random_state=int(RNG.integers(0,9999)))
        valor_usd = float(RNG.integers(3000, 95000))
        rows.append({
            "oc_id":                   f"OC-{oc_id}",
            "proveedor_id":            prov["proveedor_id"],
            "proveedor":               prov["proveedor"],
            "pais_origen":             prov["pais"],
            "moneda":                  prov["moneda"],
            "categoria":               str(prod_sel["categoria"].mode()[0]),
            "fecha_orden":             f_orden.isoformat(),
            "fecha_entrega_esperada":  f_esperada.isoformat(),
            "fecha_entrega_real":      f_real.isoformat() if f_real else None,
            "lead_time_dias":          lt,
            "estado":                  estado,
            "valor_usd":               round(valor_usd, 2),
            "valor_cop":               round(valor_usd * 4200),
            "productos":               " | ".join(prod_sel["nombre"].tolist()),
            "n_skus":                  len(prod_sel),
        })
        oc_id += 1
    pd.DataFrame(rows).to_csv(OUT/"ordenes_compra.csv", index=False)
    print(f"  ordenes_compra.csv → {len(rows)} filas")


def gen_despachos():
    clien = pd.DataFrame(CLIENTES, columns=CLI_COLS)
    sedes = pd.DataFrame(SEDES)
    rows = []
    desp_id = 8000
    today = date(2026, 8, 22)
    for i in range(580):
        dias_atras = int(RNG.integers(0, 90))
        f_pedido = today - timedelta(days=dias_atras)
        cli  = clien.sample(1, random_state=int(RNG.integers(0,9999))).iloc[0]
        sede = sedes.sample(1, random_state=int(RNG.integers(0,9999))).iloc[0]
        sla_dias = int(RNG.integers(1, 4))
        f_prometida = f_pedido + timedelta(days=sla_dias)
        cumplido = RNG.random() < 0.88
        delay = 0 if cumplido else int(RNG.integers(1, 6))
        f_entrega = f_prometida + timedelta(days=delay) if f_prometida <= today else None
        estado = ("Entregado"  if f_entrega and f_entrega <= today else
                  "En tránsito" if f_pedido <= today else "Generado")
        transito = (f_entrega - f_pedido).days if f_entrega else sla_dias
        valor = float(RNG.integers(5_000_000, 85_000_000))
        rows.append({
            "despacho_id":            f"DSP-{desp_id}",
            "fecha_pedido":           f_pedido.isoformat(),
            "fecha_entrega_prometida": f_prometida.isoformat(),
            "fecha_entrega_real":     f_entrega.isoformat() if f_entrega else None,
            "dias_transito":          transito,
            "cliente_id":             cli["cliente_id"],
            "cliente":                cli["nombre"],
            "sector":                 cli["sector"],
            "ciudad_destino":         cli["ciudad"],
            "depto_destino":          cli["depto"],
            "sede_origen":            sede["sede_id"],
            "sede_nombre":            sede["nombre"],
            "estado":                 estado,
            "entregado_a_tiempo":     cumplido if f_entrega else None,
            "valor_cop":              round(valor),
        })
        desp_id += 1
    pd.DataFrame(rows).to_csv(OUT/"despachos.csv", index=False)
    print(f"  despachos.csv → {len(rows)} filas")


def gen_grupo():
    rows = []
    empresas = [
        ("CIMPA",          1_650_000_000, 0.68, 0.14, 75),
        ("Confía Control",   320_000_000, 0.72, 0.17, 22),
        ("Vasanico",         280_000_000, 0.58, 0.10, 13),
    ]
    start = date(2025, 1, 1)
    for m in range(20):
        mes_date = start + timedelta(days=m*30)
        for emp, base_ing, margen_b, margen_ebitda, emp_count in empresas:
            factor = seasonal(mes_date.month) * (1 + 0.008 * m) * float(RNG.uniform(0.93, 1.07))
            ventas   = round(base_ing * factor)
            margen_c = round(ventas * margen_b)
            ebitda_c = round(ventas * margen_ebitda * float(RNG.uniform(0.90, 1.10)))
            cartera  = round(ventas * float(RNG.uniform(0.55, 0.85)))
            rows.append({
                "periodo":         mes_date.strftime("%Y-%m-01"),
                "empresa":         emp,
                "ventas_cop":      ventas,
                "margen_bruto_cop": margen_c,
                "ebitda_cop":      ebitda_c,
                "cartera_cop":     cartera,
                "n_empleados":     emp_count,
                "clientes_activos": int(RNG.integers(12 if emp=="CIMPA" else 5,
                                                     22 if emp=="CIMPA" else 12)),
            })
    pd.DataFrame(rows).to_csv(OUT/"grupo_mensual.csv", index=False)
    print(f"  grupo_mensual.csv → {len(rows)} filas")


if __name__ == "__main__":
    print("Generando datos CIMPA demo...")
    gen_maestros()
    gen_ventas()
    gen_inventario()
    gen_cartera()
    gen_empleados()
    gen_ordenes_compra()
    gen_despachos()
    gen_grupo()
    print("✓ Listo — todos los CSVs generados en data/")
