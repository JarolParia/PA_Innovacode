"""
app.py
------
Página principal (Home) de la aplicación Streamlit.
Solo contiene la UI — la lógica vive en etl/ y dao/.
"""

import streamlit as st
from dao.mongo_dao import MongoDAO
from etl.loader import run_etl
from services.data_service import clear_data_cache

# ─── Configuración de página ──────────────────────────────────────────────────

st.set_page_config(
    page_title="Matrículas Escolares · Antioquia",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Estilos personalizados ───────────────────────────────────────────────────

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    [data-testid="stSidebar"] {
        background-color: #1e293b;
    }
    .hero-panel {
        background: linear-gradient(135deg, rgba(15, 39, 68, 0.96), rgba(30, 58, 95, 0.92));
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 18px;
        padding: 1.5rem 1.6rem 1.35rem 1.6rem;
        box-shadow: 0 18px 40px rgba(2, 8, 23, 0.22);
        margin-bottom: 0.5rem;
    }
    .hero-kicker {
        display: inline-block;
        padding: 0.22rem 0.7rem;
        border-radius: 999px;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.28);
        color: #bae6fd;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        margin-bottom: 0.9rem;
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.08;
        margin-bottom: 0.45rem;
    }
    .hero-sub {
        color: #cbd5e1;
        font-size: 1.05rem;
        margin-bottom: 1rem;
    }
    .hero-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 0.9rem;
    }
    .hero-tag {
        display: inline-block;
        padding: 0.28rem 0.75rem;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.42);
        border: 1px solid rgba(148, 163, 184, 0.16);
        color: #e2e8f0;
        font-size: 0.82rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #0f2744);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        box-shadow: 0 14px 30px rgba(2, 8, 23, 0.16);
    }
    .metric-card h3 {
        color: #94a3b8;
        font-size: 0.85rem;
        margin: 0 0 0.4rem 0;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .metric-card p {
        color: #38bdf8;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .section-label {
        color: #e2e8f0;
        font-size: 1.12rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }
    .nav-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-left: 4px solid #38bdf8;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 10px 24px rgba(2, 8, 23, 0.12);
    }
    .nav-card h4 {
        color: #38bdf8;
        margin: 0 0 0.32rem 0;
        font-size: 1rem;
    }
    .nav-card p  {
        color: #94a3b8;
        margin: 0;
        font-size: 0.92rem;
        line-height: 1.45;
    }
    div[data-testid="stButton"] > button {
        background: linear-gradient(90deg, #0369a1, #0284c7);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.5rem;
        font-weight: 600;
        width: 100%;
        transition: 0.2s ease;
        box-shadow: 0 10px 24px rgba(3, 105, 161, 0.25);
    }
    div[data-testid="stButton"] > button:hover {
        opacity: 0.92;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-panel">
    <div class="hero-kicker">Panel principal</div>
    <div class="hero-title">🎓 Matrículas Escolares</div>
    <div class="hero-sub">
        San Pedro de los Milagros · Antioquia · 2014<br>
        Consulta rápida del comportamiento de la matrícula escolar.
    </div>
    <div class="hero-tags">
        <span class="hero-tag">SIMAT</span>
        <span class="hero-tag">Primaria</span>
        <span class="hero-tag">Datos abiertos</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ─── Sidebar: estado de conexión y carga de datos ─────────────────────────────

with st.sidebar:
  

    # ─── Estado MongoDB ────────────────────────────────────────────────
    st.markdown("### 🗄️ Estado de MongoDB")

    dao = MongoDAO()
    try:
        dao.connect()
        total_docs = dao.get_count()
        st.success("● Conectado")
        st.caption(f"Documentos en BD: **{total_docs:,}**")
    except Exception as e:
        st.error("● Sin conexión")
        st.caption("No fue posible consultar la base de datos.")
        total_docs = 0

    st.markdown("---")


    # ─── Info del proyecto ──────────────────────────────────────────────
    st.markdown("### ℹ️ Información")
    st.caption("Dataset: SIMAT · San Pedro de los Milagros · 2014")
    st.caption("Fuente: datos.gov.co")

    if dao.is_connected():
        dao.disconnect()

# ─── Métricas rápidas ─────────────────────────────────────────────────────────
def fmt_num(value, decimals=0):
    if value is None:
        return "—"
    if isinstance(value, (int, float)):
        return f"{value:,.{decimals}f}"
    return str(value)

col1, col2, col3, col4 = st.columns(4)

dao2 = MongoDAO()
resumen = {}
try:
    dao2.connect()
    from services.data_service import get_dataframe, resumen_general
    df = get_dataframe(dao2)
    resumen = resumen_general(df)
    dao2.disconnect()
except Exception:
    pass

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Total Estudiantes</h3>
        <p>{fmt_num(resumen.get('total'))}</p>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Matriculados</h3>
        <p>{fmt_num(resumen.get('matriculados'))}</p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Retirados</h3>
        <p>{fmt_num(resumen.get('retirados'))}</p>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Edad Promedio</h3>
        <p>{fmt_num(resumen.get('edad_promedio'))}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Descripción del dataset ──────────────────────────────────────────────────

st.markdown('<div class="section-label">📋 Sobre el dataset</div>', unsafe_allow_html=True)
st.markdown("""
Este conjunto de datos proviene del **Sistema Integrado de Matrícula (SIMAT)** del
Ministerio de Educación Nacional de Colombia, publicado en el portal de datos abiertos
[datos.gov.co](https://www.datos.gov.co/resource/ms9j-p68v.json).

Contiene registros de estudiantes de **primaria** del municipio de
**San Pedro de los Milagros, Antioquia**, correspondientes al año **2014**.
""")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Campos principales**")
    campos = {
        "estado": "Matrícula activa o retirado",
        "genero": "Hombre / Mujer",
        "estrato": "Estrato socioeconómico (0–4)",
        "zona_sede": "Zona Rural o Urbana",
        "grado_cod": "Grado escolar (1–5)",
        "instituci_n": "Institución educativa",
        "discapacidad": "Tipo de discapacidad reportada",
        "edad": "Calculada desde fecha de nacimiento",
    }
    for campo, desc in campos.items():
        st.markdown(f"- `{campo}`: {desc}")

with col_b:
    st.markdown("**Secciones del proyecto**")
    st.markdown("""
    <div class="nav-card">
        <h4>📊 Contexto de la BD</h4>
        <p>Resumen general de la información almacenada y una muestra de registros.</p>
    </div>
    <div class="nav-card">
        <h4>🔍 Análisis de Datos</h4>
        <p>Visualizaciones interactivas para explorar matrícula, retiro, zonas, grados e instituciones.</p>
    </div>
    <div class="nav-card">
        <h4>🗄️ Gestión de Datos</h4>
        <p>Opciones para cargar, actualizar y revisar el estado general de la información.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Fuente: datos.gov.co · Ministerio de Educación Nacional · Colombia")
