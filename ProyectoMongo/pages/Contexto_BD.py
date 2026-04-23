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
    .page-header {
        background: linear-gradient(135deg, rgba(15, 39, 68, 0.95), rgba(30, 58, 95, 0.9));
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 18px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 0.6rem;
        box-shadow: 0 18px 40px rgba(2, 8, 23, 0.2);
    }
    .page-kicker {
        display: inline-block;
        padding: 0.22rem 0.7rem;
        border-radius: 999px;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.24);
        color: #bae6fd;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    .page-title {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 0 0 0.3rem 0;
    }
    .page-sub {
        color: #cbd5e1;
        font-size: 0.98rem;
        line-height: 1.5;
    }
    .info-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1rem 1.4rem;
        box-shadow: 0 12px 28px rgba(2, 8, 23, 0.14);
    }
    .info-card h4 { color: #94a3b8; font-size: 0.8rem; text-transform: uppercase;
                    letter-spacing: 0.07em; margin: 0 0 0.3rem 0; }
    .info-card p  { color: #f1f5f9; font-size: 1.4rem; font-weight: 700; margin: 0; }
    .field-row {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid #233248;
        border-radius: 10px;
        padding: 0.55rem 0.8rem;
        margin-bottom: 0.45rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .field-name { color: #38bdf8; font-family: monospace; font-size: 0.95rem; }
    .badge {
        display: inline-block;
        padding: 0.18rem 0.62rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-green { background: #14532d; color: #4ade80; }
    .badge-yellow { background: #713f12; color: #fbbf24; }
    .badge-red { background: #7f1d1d; color: #f87171; }
    div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.75);
        border-color: #334155;
    }
</style>
""", unsafe_allow_html=True)




# ─── Conexión ─────────────────────────────────────────────────────────────────

st.markdown("""
<div class="page-header">
    <div class="page-kicker">Resumen general</div>
    <div class="page-title">📊 Contexto de la Base de Datos</div>
    <div class="page-sub">Consulta el volumen de registros, los campos disponibles y una muestra representativa de la información almacenada.</div>
</div>
""", unsafe_allow_html=True)
st.divider()

dao = MongoDAO()
try:
    dao.connect()
except Exception as e:
    st.error("❌ No fue posible conectar con la base de datos.")
    st.caption("Verifica la configuración de conexión e inténtalo nuevamente.")
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
        <h4>Registros</h4><p>{info['total_documents']:,}</p></div>""",
        unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="info-card">
        <h4>Campos</h4><p>{len(info['fields'])}</p></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Schema inferido ──────────────────────────────────────────────────────────

st.markdown("### 🗂️ Estructura de los datos")
st.caption("Campos disponibles y nivel de completitud de la información.")

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
        st.caption("10 registros de referencia")

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