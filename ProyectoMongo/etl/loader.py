"""
etl/loader.py
-------------
Extracción de datos desde la API REST de datos.gov.co,
limpieza básica e inserción en MongoDB mediante upsert.
"""

import os
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv

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


# ─── Limpieza ─────────────────────────────────────────────────────────────────

def clean_record(record: dict) -> dict:
    """
    Aplica limpieza a un registro crudo de la API:
    - Elimina campos vacíos (NR/ND)
    - Convierte fecha_nacimiento a datetime
    - Calcula edad del estudiante
    - Normaliza grado_cod a etiqueta legible
    - Normaliza tipo_de_sangre: 'NR' → None
    - Genera un _id_api único basado en el contenido del registro

    Args:
        record: Diccionario crudo proveniente de la API.

    Returns:
        Diccionario limpio listo para insertar en MongoDB.
    """
    clean = {k: v for k, v in record.items() if k not in CAMPOS_VACIOS}

    # Convertir fecha_nacimiento a datetime y calcular edad
    fecha_str = clean.get("fecha_nacimiento")
    if fecha_str:
        try:
            fecha_dt = datetime.strptime(fecha_str[:10], "%Y-%m-%d")
            clean["fecha_nacimiento"] = fecha_dt
            anio_ref = int(clean.get("a_o", datetime.now().year))
            clean["edad"] = anio_ref - fecha_dt.year
        except ValueError:
            clean["fecha_nacimiento"] = None
            clean["edad"] = None

    # Normalizar tipo_de_sangre
    if clean.get("tipo_de_sangre") in ("NR", "ND", "", None):
        clean["tipo_de_sangre"] = None

    # Normalizar grado_cod a etiqueta legible
    grado = str(clean.get("grado_cod", ""))
    clean["grado_label"] = GRADO_LABELS.get(grado, f"Grado {grado}")

    # Generar ID único reproducible basado en el contenido original
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

def fetch_all_records(progress_callback=None) -> list[dict]:
    """
    Descarga todos los registros de la API con paginación automática.

    Args:
        progress_callback: Función opcional que recibe (descargados, total_estimado)
                        para actualizar una barra de progreso.

    Returns:
        Lista de registros crudos.
    """
    all_records = []
    offset = 0

    while True:
        params = {
            "$limit": API_LIMIT,
            "$offset": offset,
        }

        try:
            response = requests.get(API_URL, params=params, timeout=30)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            print(f"[ETL] Timeout en offset {offset}. Reintentando...")
            continue
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al consumir la API: {e}")

        batch = response.json()

        if not batch:
            break  # No hay más registros

        all_records.extend(batch)

        if progress_callback:
            progress_callback(len(all_records))

        # Si el lote es menor al límite, ya llegamos al final
        if len(batch) < API_LIMIT:
            break

        offset += API_LIMIT

    return all_records


# ─── Proceso principal ────────────────────────────────────────────────────────

def run_etl(dao, progress_callback=None) -> dict:
    """
    Ejecuta el pipeline completo: extrae, limpia e inserta en MongoDB.

    Args:
        dao: Instancia de MongoDAO ya conectada.
        progress_callback: Función opcional para reportar progreso de descarga.

    Returns:
        Diccionario con estadísticas del proceso:
        {"total_api", "inserted", "modified", "errors"}
    """
    stats = {"total_api": 0, "inserted": 0, "modified": 0, "errors": 0}

    # 1. Extraer
    raw_records = fetch_all_records(progress_callback=progress_callback)
    stats["total_api"] = len(raw_records)

    if not raw_records:
        return stats

    # 2. Limpiar
    clean_records = []
    for r in raw_records:
        try:
            clean_records.append(clean_record(r))
        except Exception as e:
            print(f"[ETL] Error limpiando registro: {e}")
            stats["errors"] += 1

    # 3. Insertar / actualizar en MongoDB
    result = dao.upsert_many(clean_records, key_field="_id_api")
    stats["inserted"] = result["inserted"]
    stats["modified"] = result["modified"]

    return stats