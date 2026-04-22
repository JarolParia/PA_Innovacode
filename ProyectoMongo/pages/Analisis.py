"""
pages/2_🔍_Analisis.py
-----------------------
Página de análisis interactivo con gráficos Plotly y filtros en sidebar.
Responde preguntas de negocio concretas sobre las matrículas escolares.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dao.mongo_dao import MongoDAO
from services.data_service import (
    get_dataframe,
    conteo_por_campo,
    conteo_por_dos_campos,
    distribucion_edades,
    top_instituciones,
    resumen_general,
)

# ─── Configuración ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Análisis · Matrículas",
    page_icon="🔍",
    layout="wide",
)

# Paleta de colores consistente
COLORS = {
    "primary":    "#38bdf8",
    "secondary":  "#818cf8",
    "success":    "#4ade80",
    "warning":    "#fbbf24",
    "danger":     "#f87171",
    "bg":         "#0f172a",
    "card":       "#1e293b",
    "border":     "#334155",
    "text":       "#f1f5f9",
    "muted":      "#94a3b8",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,23,42,0.6)",
    font=dict(color=COLORS["text"], family="sans-serif"),
    xaxis=dict(gridcolor=COLORS["border"], linecolor=COLORS["border"]),
    yaxis=dict(gridcolor=COLORS["border"], linecolor=COLORS["border"]),
    margin=dict(t=50, b=40, l=40, r=20),
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    [data-testid="stSidebar"] { background-color: #1e293b; }
    .chart-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
    }
    .chart-title {
        color: #f1f5f9;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .chart-question {
        color: #94a3b8;
        font-size: 0.82rem;
        font-style: italic;
        margin-bottom: 0.8rem;
    }
    .kpi-box {
        background: linear-gradient(135deg, #1e3a5f, #0f2744);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        text-align: center;
    }
    .kpi-box h4 { color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;
                letter-spacing: 0.07em; margin: 0 0 0.3rem 0; }
    .kpi-box p  { color: #38bdf8; font-size: 1.6rem; font-weight: 700; margin: 0; }
</style>
""", unsafe_allow_html=True)

# ─── Conexión ─────────────────────────────────────────────────────────────────

dao = MongoDAO()
try:
    dao.connect()
except Exception as e:
    st.error(f"❌ No se pudo conectar a MongoDB: {e}")
    st.stop()

df_base = get_dataframe(dao)

if df_base.empty:
    st.warning("⚠️ No hay datos disponibles. Ve al Inicio y presiona 'Cargar datos'.")
    dao.disconnect()
    st.stop()

# ─── Sidebar: filtros ─────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🔍 Filtros")
    st.caption("Los filtros aplican a todos los gráficos.")

    estado_opts = ["Todos"] + sorted(df_base["estado"].dropna().unique().tolist())
    sel_estado = st.selectbox("Estado", estado_opts)

    genero_opts = ["Todos"] + sorted(df_base["genero"].dropna().unique().tolist())
    sel_genero = st.selectbox("Género", genero_opts)

    zona_opts = ["Todos"] + sorted(df_base["zona_sede"].dropna().unique().tolist())
    sel_zona = st.selectbox("Zona", zona_opts)

    estrato_opts = ["Todos"] + sorted(df_base["estrato"].dropna().unique().tolist())
    sel_estrato = st.selectbox("Estrato", estrato_opts)

    inst_opts = ["Todas"] + sorted(df_base["instituci_n"].dropna().unique().tolist())
    sel_inst = st.selectbox("Institución", inst_opts)

    st.markdown("---")
    st.page_link("app.py",                           label="🏠 Inicio")
    st.page_link("pages/Contexto_BD.py",        label="📊 Contexto de la BD")
    st.page_link("pages/Analisis.py",           label="🔍 Análisis de Datos")

# ─── Aplicar filtros ──────────────────────────────────────────────────────────

df = df_base.copy()
if sel_estado  != "Todos":  df = df[df["estado"]      == sel_estado]
if sel_genero  != "Todos":  df = df[df["genero"]      == sel_genero]
if sel_zona    != "Todos":  df = df[df["zona_sede"]   == sel_zona]
if sel_estrato != "Todos":  df = df[df["estrato"]     == sel_estrato]
if sel_inst    != "Todas":  df = df[df["instituci_n"] == sel_inst]

# ─── Encabezado ───────────────────────────────────────────────────────────────

st.markdown("## 🔍 Análisis de Matrículas Escolares")
st.caption(f"Mostrando **{len(df):,}** registros con los filtros seleccionados.")
st.divider()

# ─── KPIs del subset filtrado ─────────────────────────────────────────────────

resumen = resumen_general(df)
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f'<div class="kpi-box"><h4>Estudiantes</h4><p>{resumen.get("total",0):,}</p></div>',
                unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-box"><h4>Matriculados</h4><p>{resumen.get("matriculados",0):,}</p></div>',
                unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-box"><h4>Retirados</h4><p>{resumen.get("retirados",0):,}</p></div>',
                unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-box"><h4>Con Discapacidad</h4><p>{resumen.get("con_discapacidad",0):,}</p></div>',
                unsafe_allow_html=True)
with k5:
    st.markdown(f'<div class="kpi-box"><h4>Edad Promedio</h4><p>{resumen.get("edad_promedio","—")}</p></div>',
                unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Fila 1: Gráfico de barras estrato×género  |  Instituciones top ───────────

col1, col2 = st.columns([1.1, 0.9])

with col1:
    st.markdown('<div class="chart-title">👥 Distribución por Estrato y Género</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-question">¿Cómo se distribuyen los estudiantes por estrato socioeconómico según su género?</div>', unsafe_allow_html=True)

    df_eg = conteo_por_dos_campos(df, "estrato", "genero")
    if not df_eg.empty:
        fig = px.bar(
            df_eg, x="estrato", y="cantidad", color="genero",
            barmode="group",
            color_discrete_map={"HOMBRE": COLORS["primary"], "MUJER": COLORS["secondary"]},
            labels={"estrato": "Estrato", "cantidad": "Estudiantes", "genero": "Género"},
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin datos para este filtro.")

with col2:
    st.markdown('<div class="chart-title">🏫 Top Instituciones por Número de Estudiantes</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-question">¿Qué instituciones concentran la mayor población estudiantil?</div>', unsafe_allow_html=True)

    df_inst = top_instituciones(df, top_n=8)
    if not df_inst.empty:
        fig2 = px.bar(
            df_inst.sort_values("cantidad"),
            x="cantidad", y="instituci_n",
            orientation="h",
            color="cantidad",
            color_continuous_scale=["#1e3a5f", "#38bdf8"],
            labels={"cantidad": "Estudiantes", "instituci_n": "Institución"},
        )
        fig2.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False,
                        yaxis_title="", xaxis_title="Estudiantes")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sin datos para este filtro.")

# ─── Fila 2: Zona×Grado apilado  |  Discapacidad donut ───────────────────────

col3, col4 = st.columns([1.2, 0.8])

with col3:
    st.markdown('<div class="chart-title">📚 Estudiantes por Grado y Zona</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-question">¿Cómo varía la distribución de grados entre la zona rural y urbana?</div>', unsafe_allow_html=True)

    df_gz = conteo_por_dos_campos(df, "grado_label", "zona_sede")
    if not df_gz.empty:
        fig3 = px.bar(
            df_gz, x="grado_label", y="cantidad", color="zona_sede",
            barmode="stack",
            color_discrete_map={"RURAL": COLORS["warning"], "URBANA": COLORS["success"]},
            labels={"grado_label": "Grado", "cantidad": "Estudiantes", "zona_sede": "Zona"},
        )
        fig3.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Sin datos para este filtro.")

with col4:
    st.markdown('<div class="chart-title">♿ Tipos de Discapacidad</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-question">¿Qué proporción de estudiantes presenta algún tipo de discapacidad?</div>', unsafe_allow_html=True)

    df_disc = conteo_por_campo(df, "discapacidad")
    if not df_disc.empty:
        colores_disc = [
            COLORS["muted"], COLORS["primary"], COLORS["secondary"],
            COLORS["warning"], COLORS["danger"], COLORS["success"],
        ]
        fig4 = go.Figure(go.Pie(
            labels=df_disc["discapacidad"],
            values=df_disc["cantidad"],
            hole=0.55,
            marker_colors=colores_disc,
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>%{value} estudiantes<br>%{percent}<extra></extra>",
        ))
        fig4.update_layout(
            **PLOTLY_LAYOUT,
            legend=dict(font=dict(size=10), orientation="v"),
            annotations=[dict(
                text=f"<b>{len(df):,}</b><br>total",
                x=0.5, y=0.5, font_size=13,
                font_color=COLORS["text"],
                showarrow=False,
            )],
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Sin datos para este filtro.")

# ─── Fila 3: Histograma de edades  |  Estado por estrato ─────────────────────

col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="chart-title">📅 Distribución de Edades</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-question">¿Cuál es el rango de edades de los estudiantes matriculados?</div>', unsafe_allow_html=True)

    df_edad = distribucion_edades(df)
    if not df_edad.empty:
        fig5 = px.histogram(
            df_edad, x="edad", nbins=15,
            color_discrete_sequence=[COLORS["primary"]],
            labels={"edad": "Edad (años)", "count": "Cantidad"},
        )
        fig5.update_traces(marker_line_color=COLORS["bg"], marker_line_width=1.5)
        fig5.update_layout(**PLOTLY_LAYOUT, bargap=0.05)
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Sin datos de edad disponibles.")

with col6:
    st.markdown('<div class="chart-title">📋 Estado de Matrícula por Estrato</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-question">¿En qué estratos hay mayor tasa de retiro escolar?</div>', unsafe_allow_html=True)

    df_est = conteo_por_dos_campos(df, "estrato", "estado")
    if not df_est.empty:
        fig6 = px.bar(
            df_est, x="estrato", y="cantidad", color="estado",
            barmode="group",
            color_discrete_map={
                "MATRICULADO": COLORS["success"],
                "RETIRADO":    COLORS["danger"],
            },
            labels={"estrato": "Estrato", "cantidad": "Estudiantes", "estado": "Estado"},
        )
        fig6.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("Sin datos para este filtro.")

# ─── Cierre ───────────────────────────────────────────────────────────────────

dao.disconnect()
st.markdown("---")
st.caption("Fuente: datos.gov.co · SIMAT · Ministerio de Educación Nacional · Colombia")