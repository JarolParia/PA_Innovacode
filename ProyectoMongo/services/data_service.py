"""
services/data_service.py
------------------------
Lógica de negocio y transformaciones sobre los datos.
Recibe listas de documentos desde el DAO y retorna
DataFrames de pandas listos para graficar.
"""

import pandas as pd
from dao.mongo_dao import MongoDAO


# ─── Carga de datos ───────────────────────────────────────────────────────────

def get_dataframe(dao: MongoDAO, filters: dict = None) -> pd.DataFrame:
    """
    Obtiene todos los registros del DAO y los convierte a DataFrame.

    Args:
        dao: Instancia de MongoDAO conectada.
        filters: Filtros MongoDB opcionales.

    Returns:
        DataFrame con los datos limpios.
    """
    records = dao.get_all(filters=filters)
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    # Asegurar tipos correctos
    if "fecha_nacimiento" in df.columns:
        df["fecha_nacimiento"] = pd.to_datetime(df["fecha_nacimiento"], errors="coerce")

    if "edad" in df.columns:
        df["edad"] = pd.to_numeric(df["edad"], errors="coerce")

    if "grado_cod" in df.columns:
        df["grado_cod"] = df["grado_cod"].astype(str)

    return df


# ─── Agregaciones para gráficos ───────────────────────────────────────────────

def conteo_por_campo(df: pd.DataFrame, campo: str) -> pd.DataFrame:
    """
    Cuenta registros agrupados por un campo categórico.

    Returns:
        DataFrame con columnas [campo, 'cantidad'].
    """
    if df.empty or campo not in df.columns:
        return pd.DataFrame(columns=[campo, "cantidad"])

    return (
        df.groupby(campo)
        .size()
        .reset_index(name="cantidad")
        .sort_values("cantidad", ascending=False)
    )


def conteo_por_dos_campos(df: pd.DataFrame, campo1: str, campo2: str) -> pd.DataFrame:
    """
    Cuenta registros agrupados por dos campos (útil para barras agrupadas).

    Returns:
        DataFrame con columnas [campo1, campo2, 'cantidad'].
    """
    if df.empty:
        return pd.DataFrame(columns=[campo1, campo2, "cantidad"])

    return (
        df.groupby([campo1, campo2])
        .size()
        .reset_index(name="cantidad")
        .sort_values(campo1)
    )


def distribucion_edades(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra y retorna el campo edad para histograma,
    excluyendo valores atípicos (menores de 4 o mayores de 20).

    Returns:
        DataFrame con columna 'edad' limpia.
    """
    if df.empty or "edad" not in df.columns:
        return pd.DataFrame(columns=["edad"])

    return df[df["edad"].between(4, 20)][["edad"]].dropna()


def top_instituciones(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Retorna las N instituciones con más estudiantes.

    Returns:
        DataFrame con columnas ['instituci_n', 'cantidad'].
    """
    if df.empty or "instituci_n" not in df.columns:
        return pd.DataFrame(columns=["instituci_n", "cantidad"])

    return (
        df.groupby("instituci_n")
        .size()
        .reset_index(name="cantidad")
        .sort_values("cantidad", ascending=False)
        .head(top_n)
    )


def resumen_general(df: pd.DataFrame) -> dict:
    """
    Calcula métricas generales del dataset para mostrar en tarjetas.

    Returns:
        Diccionario con métricas clave.
    """
    if df.empty:
        return {}

    total = len(df)
    matriculados = len(df[df["estado"] == "MATRICULADO"]) if "estado" in df.columns else 0
    retirados = len(df[df["estado"] == "RETIRADO"]) if "estado" in df.columns else 0
    con_discapacidad = len(df[df["discapacidad"] != "NO APLICA"]) if "discapacidad" in df.columns else 0
    edad_promedio = round(df["edad"].mean(), 1) if "edad" in df.columns else "N/A"

    return {
        "total": total,
        "matriculados": matriculados,
        "retirados": retirados,
        "con_discapacidad": con_discapacidad,
        "edad_promedio": edad_promedio,
        "pct_retirados": round(retirados / total * 100, 1) if total > 0 else 0,
    }