"""
pages/Gestion_Datos.py
----------------------
Página para cargar, sincronizar y actualizar la base de datos.
Mantiene el estilo original del proyecto.
"""

from datetime import datetime

import streamlit as st

from dao.mongo_dao import MongoDAO
from etl.loader import full_reload, run_etl
from services.data_service import clear_data_cache


st.set_page_config(
    page_title="Gestión de Datos · Matrículas",
    page_icon="🗄️",
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
    .info-card h4 {
        color: #94a3b8;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin: 0 0 0.3rem 0;
    }
    .info-card p {
        color: #f1f5f9;
        font-size: 1.15rem;
        font-weight: 700;
        margin: 0;
    }
    .panel-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 12px 28px rgba(2, 8, 23, 0.12);
    }
    .panel-card h4 {
        color: #38bdf8;
        margin: 0 0 0.5rem 0;
    }
    .small-note {
        color: #94a3b8;
        font-size: 0.92rem;
        margin-top: 0.3rem;
        line-height: 1.45;
    }
    .log-box {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        color: #e2e8f0;
        min-height: 140px;
    }
    .detail-row {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        align-items: center;
        padding: 0.62rem 0;
        border-bottom: 1px solid rgba(148, 163, 184, 0.12);
    }
    .detail-row:last-child { border-bottom: none; }
    .detail-label { color: #94a3b8; font-size: 0.9rem; }
    .detail-value { color: #f8fafc; font-weight: 600; text-align: right; }
    div[data-baseweb="checkbox"] label span,
    div[data-baseweb="checkbox"] > label span {
        color: #e2e8f0;
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


def fmt_num(value, decimals=0):
    if value is None:
        return "—"
    if isinstance(value, (int, float)):
        return f"{value:,.{decimals}f}"
    return str(value)


def fmt_dt(value):
    if not value:
        return "Sin registro"
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(value)


def ejecutar_con_feedback(dao, *, full=False, prune_missing=True, only_if_changed=True):
    logs = []
    log_box = st.empty()

    def progress_callback(event: dict):
        message = event.get("message")
        if not message:
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        logs.append(f"[{timestamp}] {message}")
        log_box.markdown(
            '<div class="log-box">' + '<br>'.join(logs[-10:]) + '</div>',
            unsafe_allow_html=True,
        )

    with st.spinner("Procesando actualización de datos..."):
        if full:
            stats = full_reload(dao, progress_callback=progress_callback)
        else:
            stats = run_etl(
                dao,
                progress_callback=progress_callback,
                prune_missing=prune_missing,
                only_if_changed=only_if_changed,
            )

    clear_data_cache()
    return stats


st.markdown("""
<div class="page-header">
    <div class="page-kicker">Control de datos</div>
    <div class="page-title">🗄️ Gestión de Datos</div>
    <div class="page-sub">Desde esta vista puedes actualizar la información, revisar el estado actual y consultar el último proceso ejecutado.</div>
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

meta = dao.get_sync_metadata()
total_docs = dao.get_count()

c1, c2, c3, c4 = st.columns(4)
with c1:
    estado = "Conectado" if dao.is_connected() else "Sin conexión"
    st.markdown(f"<div class=\"info-card\"><h4>Estado MongoDB</h4><p>{estado}</p></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class=\"info-card\"><h4>Documentos</h4><p>{fmt_num(total_docs)}</p></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class=\"info-card\"><h4>Última actualización</h4><p>{fmt_dt(meta.get('last_sync_finished_at'))}</p></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class=\"info-card\"><h4>Errores última carga</h4><p>{fmt_num(meta.get('last_errors', 0))}</p></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

res_flash = st.session_state.pop("gestion_datos_resultado", None)
if res_flash is not None:
    if res_flash.get("skipped"):
        st.info(res_flash.get("message", "No se encontraron cambios para actualizar."))
    else:
        st.success(res_flash.get("message", "Proceso completado correctamente."))

    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("Total API", fmt_num(res_flash.get("total_api", 0)))
    r2.metric("Insertados", fmt_num(res_flash.get("inserted", 0)))
    r3.metric("Modificados", fmt_num(res_flash.get("modified", 0)))
    r4.metric("Eliminados", fmt_num(res_flash.get("deleted", 0)))
    r5.metric("Errores", fmt_num(res_flash.get("errors", 0)))
    st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns([1.1, 0.9])

with left:
    st.markdown('<div class="panel-card"><h4>🔄 Opciones de actualización</h4><div class="small-note">Selecciona la acción que deseas ejecutar sobre la información disponible.</div></div>', unsafe_allow_html=True)

    prune_missing = st.checkbox(
        "Eliminar registros que ya no estén disponibles",
        value=True,
        help="Quita registros que ya no aparezcan en la fuente de datos.",
    )
    only_if_changed = st.checkbox(
        "Comprobar si existen cambios antes de actualizar",
        value=True,
        help="Evita ejecutar una actualización si la fuente no reporta novedades.",
    )
    auto_sync = st.checkbox(
        "Actualizar automáticamente al abrir esta vista",
        value=False,
        help="Se ejecuta una sola vez por sesión mientras esta vista permanezca abierta.",
    )

    b1, b2, b3 = st.columns(3)
    run_smart = b1.button("📥 Actualizar", use_container_width=True)
    run_full = b2.button("🧹 Recargar todo", use_container_width=True)
    clean_cache = b3.button("🧼 Refrescar vista", use_container_width=True)

    if clean_cache:
        clear_data_cache()
        st.success("La vista se actualizó correctamente.")

    auto_key = "_gestion_auto_sync_done"
    if not auto_sync:
        st.session_state[auto_key] = False

    stats = None
    should_auto_run = auto_sync and not st.session_state.get(auto_key, False)
    if should_auto_run:
        st.session_state[auto_key] = True
        stats = ejecutar_con_feedback(
            dao,
            full=False,
            prune_missing=prune_missing,
            only_if_changed=only_if_changed,
        )
    elif run_smart:
        stats = ejecutar_con_feedback(
            dao,
            full=False,
            prune_missing=prune_missing,
            only_if_changed=only_if_changed,
        )
    elif run_full:
        stats = ejecutar_con_feedback(
            dao,
            full=True,
            prune_missing=False,
            only_if_changed=False,
        )

    if stats is not None:
        st.session_state["gestion_datos_resultado"] = stats
        st.rerun()

with right:
    st.markdown('<div class="panel-card"><h4>📝 Última actualización registrada</h4><div class="small-note">Consulta el resumen más reciente de la carga de datos.</div></div>', unsafe_allow_html=True)
    if meta:
        detail_rows = [
            ("Inicio", fmt_dt(meta.get("last_sync_started_at"))),
            ("Finalización", fmt_dt(meta.get("last_sync_finished_at"))),
            ("Registros procesados", fmt_num(meta.get("last_total_api", 0))),
            ("Insertados", fmt_num(meta.get("last_inserted", 0))),
            ("Actualizados", fmt_num(meta.get("last_modified", 0))),
            ("Eliminados", fmt_num(meta.get("last_deleted", 0))),
            ("Errores", fmt_num(meta.get("last_errors", 0))),
        ]
        detail_html = "".join(
            f'<div class="detail-row"><span class="detail-label">{label}</span><span class="detail-value">{value}</span></div>'
            for label, value in detail_rows
        )
        st.markdown(f'<div class="panel-card">{detail_html}</div>', unsafe_allow_html=True)
    else:
        st.info("Aún no hay información registrada. Ejecuta una actualización para verla aquí.")

st.markdown("---")
st.caption("Fuente: datos.gov.co · SIMAT · Ministerio de Educación Nacional · Colombia")

dao.disconnect()
