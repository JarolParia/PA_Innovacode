"""
etl/loader.py
-------------
Extracción de datos desde la API REST de datos.gov.co,
limpieza básica e inserción en MongoDB mediante una sincronización más eficiente.
"""

import os
import hashlib
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

# ─── Constantes ──────────────────────────────────────────────────────────────

API_URL = os.getenv("API_URL", "https://www.datos.gov.co/resource/ms9j-p68v.json")
API_LIMIT = int(os.getenv("API_LIMIT", 5000))

# Campos que se eliminan por tener 99-100% de valores vacíos/NR
CAMPOS_VACIOS = {"eps", "jornada", "sisben_iv", "pais_origen"}

# Mapeo de grados especiales a etiquetas legibles
GRADO_LABELS = {
    "1": "Grado 1", "2": "Grado 2", "3": "Grado 3",
    "4": "Grado 4", "5": "Grado 5",
    "22": "Ciclo 2", "99": "Extraedad / Sin Clasificar",
}


def build_session() -> requests.Session:
    """Crea una sesión HTTP con reintentos automáticos."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[408, 429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET"]),
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "ProyectoMongo/2.0"})
    return session


def notify(progress_callback=None, **payload):
    """Envía mensajes de progreso si se proporciona callback."""
    if progress_callback:
        progress_callback(payload)


# ─── Limpieza ─────────────────────────────────────────────────────────────────

def clean_record(record: dict) -> dict:
    """
    Aplica limpieza a un registro crudo de la API.
    """
    clean = {k: v for k, v in record.items() if k not in CAMPOS_VACIOS}

    fecha_str = clean.get("fecha_nacimiento")
    if fecha_str:
        try:
            fecha_dt = datetime.strptime(str(fecha_str)[:10], "%Y-%m-%d")
            clean["fecha_nacimiento"] = fecha_dt
            anio_ref = int(clean.get("a_o", datetime.now().year))
            clean["edad"] = anio_ref - fecha_dt.year
        except ValueError:
            clean["fecha_nacimiento"] = None
            clean["edad"] = None

    if clean.get("tipo_de_sangre") in ("NR", "ND", "", None):
        clean["tipo_de_sangre"] = None

    grado = str(clean.get("grado_cod", ""))
    clean["grado_label"] = GRADO_LABELS.get(grado, f"Grado {grado}" if grado else "Sin grado")

    unique_fields = [
        str(record.get("documento", "")),
        str(record.get("instituci_n", "")),
        str(record.get("grado_cod", "")),
        str(record.get("fecha_nacimiento", "")),
        str(record.get("a_o", "")),
    ]
    raw_id = "|".join(unique_fields)
    clean["_id_api"] = hashlib.md5(raw_id.encode()).hexdigest()

    return clean


# ─── Extracción ───────────────────────────────────────────────────────────────

def fetch_source_signature(session=None) -> dict:
    """Obtiene metadatos de la fuente para detectar posibles cambios."""
    session = session or build_session()
    response = session.get(API_URL, params={"$limit": 1}, timeout=(10, 30))
    response.raise_for_status()
    return {
        "source_etag": response.headers.get("ETag"),
        "source_last_modified": response.headers.get("Last-Modified"),
    }


def fetch_record_batches(progress_callback=None, session=None):
    """Descarga los registros por lotes para reducir el uso de memoria."""
    session = session or build_session()
    offset = 0
    downloaded = 0

    while True:
        response = session.get(
            API_URL,
            params={"$limit": API_LIMIT, "$offset": offset},
            timeout=(10, 60),
        )
        response.raise_for_status()
        batch = response.json()

        if not batch:
            break

        downloaded += len(batch)
        notify(
            progress_callback,
            stage="download",
            processed=downloaded,
            batch_size=len(batch),
            message=f"Descargados {downloaded:,} registros desde la API.",
        )
        yield batch

        if len(batch) < API_LIMIT:
            break

        offset += API_LIMIT


# ─── Proceso principal ────────────────────────────────────────────────────────

def run_etl(dao, progress_callback=None, prune_missing=True, only_if_changed=False) -> dict:
    """
    Ejecuta el pipeline completo: extrae, limpia y sincroniza en MongoDB.
    A diferencia de la versión anterior, no borra toda la colección al inicio.
    """
    stats = {
        "total_api": 0,
        "inserted": 0,
        "modified": 0,
        "deleted": 0,
        "errors": 0,
        "skipped": False,
        "message": "",
    }

    sync_started_at = datetime.now(timezone.utc)
    session = build_session()

    notify(progress_callback, stage="prepare", message="Preparando sincronización e índices...")
    source_signature = fetch_source_signature(session)
    previous_meta = dao.get_sync_metadata()

    if only_if_changed:
        same_etag = bool(source_signature.get("source_etag")) and source_signature.get("source_etag") == previous_meta.get("source_etag")
        same_last_modified = bool(source_signature.get("source_last_modified")) and source_signature.get("source_last_modified") == previous_meta.get("source_last_modified")
        if same_etag or same_last_modified:
            stats["skipped"] = True
            stats["message"] = "La fuente no reporta cambios; se omitió la sincronización."
            notify(progress_callback, stage="skipped", message=stats["message"])
            return stats

    sync_token = sync_started_at.isoformat()
    processed = 0

    for raw_batch in fetch_record_batches(progress_callback=progress_callback, session=session):
        clean_batch = []

        for record in raw_batch:
            try:
                doc = clean_record(record)
                doc["_sync_token"] = sync_token
                clean_batch.append(doc)
            except Exception as e:
                print(f"[ETL] Error limpiando registro: {e}")
                stats["errors"] += 1

        batch_result = dao.upsert_many(clean_batch, key_field="_id_api")
        stats["inserted"] += batch_result["inserted"]
        stats["modified"] += batch_result["modified"]
        stats["total_api"] += len(raw_batch)
        processed += len(clean_batch)

        notify(
            progress_callback,
            stage="upsert",
            processed=processed,
            batch_size=len(clean_batch),
            message=(
                f"Sincronizados {processed:,} registros | "
                f"Insertados: {stats['inserted']:,} | "
                f"Modificados: {stats['modified']:,}"
            ),
        )

    if prune_missing:
        notify(progress_callback, stage="cleanup", message="Eliminando registros obsoletos...")
        stats["deleted"] = dao.delete_stale_records(sync_token)

    sync_finished_at = datetime.now(timezone.utc)
    dao.save_sync_metadata({
        "last_sync_started_at": sync_started_at.isoformat(),
        "last_sync_finished_at": sync_finished_at.isoformat(),
        "last_sync_mode": "smart-sync",
        "last_total_api": stats["total_api"],
        "last_inserted": stats["inserted"],
        "last_modified": stats["modified"],
        "last_deleted": stats["deleted"],
        "last_errors": stats["errors"],
        **source_signature,
    })

    stats["message"] = "Sincronización finalizada correctamente."
    notify(progress_callback, stage="done", message=stats["message"])
    return stats


def full_reload(dao, progress_callback=None) -> dict:
    """Fuerza una recarga completa cuando el usuario lo necesite."""
    notify(progress_callback, stage="prepare", message="Eliminando datos actuales antes de recargar...")
    deleted_before = dao.delete_all()
    stats = run_etl(dao, progress_callback=progress_callback, prune_missing=False, only_if_changed=False)
    stats["deleted_before_reload"] = deleted_before
    return stats
