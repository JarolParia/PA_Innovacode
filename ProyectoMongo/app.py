"""
app.py
------
Página principal (Home) de la aplicación Streamlit.
Solo contiene la UI — la lógica vive en etl/ y dao/.
"""

import streamlit as st
from dao.mongo_dao import MongoDAO
from etl.loader import run_etl

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
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #0f2744);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
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
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #f1f5f9;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .nav-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .nav-card h4 { color: #38bdf8; margin: 0 0 0.3rem 0; }
    .nav-card p  { color: #94a3b8; margin: 0; font-size: 0.9rem; }
    .status-ok   { color: #4ade80; font-weight: 600; }
    .status-err  { color: #f87171; font-weight: 600; }
    div[data-testid="stButton"] > button {
        background: linear-gradient(90deg, #0369a1, #0284c7);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        width: 100%;
        transition: opacity 0.2s;
    }
    div[data-testid="stButton"] > button:hover { opacity: 0.85; }
</style>
""", unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-title">🎓 Matrículas Escolares</div>
<div class="hero-sub">
    San Pedro de los Milagros · Antioquia · 2014<br>
    Datos abiertos del Ministerio de Educación Nacional de Colombia
</div>
""", unsafe_allow_html=True)

st.divider()

# ─── Sidebar: estado de conexión y carga de datos ─────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Panel de Control")
    st.caption("Gestión de datos y estado del sistema")

    st.markdown("---")

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
        st.caption(str(e))
        total_docs = 0

    st.markdown("---")

    # ─── Actualizar datos ───────────────────────────────────────────────
    st.markdown("### 🔄 Actualizar datos")
    st.caption("Consume la API y actualiza la colección en MongoDB.")

    if st.button("📥 Cargar / Actualizar datos"):
        if not dao.is_connected():
            st.error("No hay conexión con MongoDB.")
        else:
            try:
                with st.spinner("Eliminando datos anteriores..."):
                    deleted = dao.delete_all()

                with st.spinner("Descargando datos desde la API..."):
                    stats = run_etl(dao)

                st.success("Carga completada correctamente ✅")
                st.info(
                    f"📊 Total API: {stats['total_api']:,}\n"
                    f"🗑️ Eliminados: {deleted:,}\n"
                    f"📥 Insertados: {stats['inserted']:,}\n"
                    f"✏️ Modificados: {stats['modified']:,}\n"
                    f"⚠️ Errores: {stats['errors']:,}"
                )

                st.rerun()

            except Exception as e:
                st.error(f"Error en ETL: {e}")

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

st.markdown("### 📋 Sobre el dataset")
st.markdown("""
Este conjunto de datos proviene del **Sistema Integrado de Matrícula (SIMAT)** del
Ministerio de Educación Nacional de Colombia, publicado en el portal de datos abiertos
[datos.gov.co](https://www.datos.gov.co/resource/ms9j-p68v.json).

Contiene registros de estudiantes de **primaria** del municipio de
**San Pedro de los Milagros, Antioquia**, correspondientes al año **2014**.
""")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Campos principales analizados:**")
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
    st.markdown("**Navegación del proyecto:**")
    st.markdown("""
    <div class="nav-card">
        <h4>📊 Contexto de la BD</h4>
        <p>Información técnica de la base de datos: colección, total de documentos,
        schema inferido y muestra de registros.</p>
    </div>
    <div class="nav-card">
        <h4>🔍 Análisis de Datos</h4>
        <p>Gráficos interactivos con filtros por estado, género, zona, estrato e institución.
        Responde preguntas clave sobre la población estudiantil.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Fuente: datos.gov.co · Ministerio de Educación Nacional · Colombia")