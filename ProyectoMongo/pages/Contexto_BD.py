"""
pages/1_📊_Contexto_BD.py
--------------------------
Página de contexto técnico de la base de datos MongoDB.
Muestra metadata, schema inferido y muestra de documentos.
"""

import streamlit as st
import pandas as pd
from dao.mongo_dao import MongoDAO

# ─── Configuración ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Contexto BD · Matrículas",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    [data-testid="stSidebar"] { background-color: #1e293b; }
    .info-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1rem 1.4rem;
    }
    .info-card h4 { color: #94a3b8; font-size: 0.8rem; text-transform: uppercase;
                    letter-spacing: 0.07em; margin: 0 0 0.3rem 0; }
    .info-card p  { color: #f1f5f9; font-size: 1.4rem; font-weight: 700; margin: 0; }
    .field-row {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 0.5rem 0.8rem;
        margin-bottom: 0.4rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .field-name { color: #38bdf8; font-family: monospace; font-size: 0.95rem; }
    .field-type { color: #64748b; font-size: 0.8rem; }
    .badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-green { background: #14532d; color: #4ade80; }
    .badge-yellow { background: #713f12; color: #fbbf24; }
    .badge-red { background: #7f1d1d; color: #f87171; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Panel de Control")
    st.markdown("---")
    st.page_link("app.py",                           label="🏠 Inicio")
    st.page_link("pages/Contexto_BD.py",        label="📊 Contexto de la BD")
    st.page_link("pages/Analisis.py",           label="🔍 Análisis de Datos")

# ─── Conexión ─────────────────────────────────────────────────────────────────

st.markdown("## 📊 Contexto de la Base de Datos")
st.caption("Información técnica sobre la colección MongoDB y los datos almacenados.")
st.divider()

dao = MongoDAO()
try:
    dao.connect()
except Exception as e:
    st.error(f"❌ No se pudo conectar a MongoDB: {e}")
    st.stop()

# ─── Métricas de la colección ─────────────────────────────────────────────────

info = dao.get_collection_info()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="info-card">
        <h4>Base de Datos</h4><p>{info['db_name']}</p></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="info-card">
        <h4>Colección</h4><p>{info['collection_name']}</p></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="info-card">
        <h4>Total Documentos</h4><p>{info['total_documents']:,}</p></div>""",
        unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="info-card">
        <h4>Campos por Doc.</h4><p>{len(info['fields'])}</p></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Schema inferido ──────────────────────────────────────────────────────────

st.markdown("### 🗂️ Schema de la colección")
st.caption("Campos disponibles, tipo de dato y porcentaje de completitud.")

# Cargar sample para inferir tipos y nulos
from services.data_service import get_dataframe
df_full = get_dataframe(dao)

if not df_full.empty:
    col_schema, col_sample = st.columns([1, 2])

    with col_schema:
        total = len(df_full)
        for col in df_full.columns:
            dtype = str(df_full[col].dtype)
            nulos = df_full[col].isna().sum() + (df_full[col] == "NR").sum()
            pct_ok = round((1 - nulos / total) * 100)

            if pct_ok >= 90:
                badge = '<span class="badge badge-green">✓ {}%</span>'.format(pct_ok)
            elif pct_ok >= 50:
                badge = '<span class="badge badge-yellow">⚠ {}%</span>'.format(pct_ok)
            else:
                badge = '<span class="badge badge-red">✗ {}%</span>'.format(pct_ok)

            st.markdown(f"""
            <div class="field-row">
                <span class="field-name">{col}</span>
                <span>{badge}</span>
            </div>""", unsafe_allow_html=True)

    with col_sample:
        st.markdown("### 👁️ Muestra de documentos")
        st.caption("10 registros aleatorios de la colección")

        sample_docs = dao.get_sample(10)
        if sample_docs:
            df_sample = pd.DataFrame(sample_docs)
            # Formatear fecha para visualización
            if "fecha_nacimiento" in df_sample.columns:
                df_sample["fecha_nacimiento"] = pd.to_datetime(
                    df_sample["fecha_nacimiento"], errors="coerce"
                ).dt.strftime("%Y-%m-%d")
            st.dataframe(
                df_sample,
                use_container_width=True,
                height=380,
                hide_index=True,
            )
else:
    st.warning("⚠️ No hay datos en la colección. Ve al Inicio y presiona 'Cargar datos'.")

st.divider()

# ─── Valores únicos por campo categórico ──────────────────────────────────────

st.markdown("### 🔎 Valores únicos por campo")
st.caption("Distribución de categorías en los campos más relevantes.")

campos_cat = ["estado", "genero", "zona_sede", "nivel", "estrato", "discapacidad", "grado_label"]

if not df_full.empty:
    cols = st.columns(3)
    for i, campo in enumerate(campos_cat):
        if campo in df_full.columns:
            with cols[i % 3]:
                conteo = df_full[campo].value_counts().reset_index()
                conteo.columns = [campo, "cantidad"]
                st.markdown(f"**`{campo}`**")
                st.dataframe(conteo, use_container_width=True, hide_index=True, height=180)

dao.disconnect()

st.markdown("---")
st.caption("Fuente: datos.gov.co · SIMAT · Ministerio de Educación Nacional · Colombia")