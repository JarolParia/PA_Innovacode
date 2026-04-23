"""
dao/mongo_dao.py
----------------
Capa de acceso a datos (DAO) para MongoDB.
Toda interacción con la base de datos pasa por esta clase.
"""

import os
from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure, BulkWriteError, OperationFailure

load_dotenv()


class MongoDAO:
    """Gestiona la conexión y operaciones CRUD sobre MongoDB."""

    def __init__(self):
        self._client = None
        self._db = None
        self._collection = None
        self._meta = None

    def connect(self):
        """Establece conexión con MongoDB usando variables de entorno."""
        uri = os.getenv("MONGO_URI")
        db_name = os.getenv("DB_NAME", "matriculas_antioquia")
        collection_name = os.getenv("COLLECTION_NAME", "estudiantes")

        if not uri:
            raise ValueError("MONGO_URI no está definida en las variables de entorno.")

        self._client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self._client.admin.command("ping")
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]
        self._meta = self._db["_app_metadata"]
        self.ensure_indexes()

    def disconnect(self):
        """Cierra la conexión con MongoDB."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            self._collection = None
            self._meta = None

    def is_connected(self) -> bool:
        """Retorna True si hay una conexión activa."""
        try:
            if self._client:
                self._client.admin.command("ping")
                return True
        except ConnectionFailure:
            pass
        return False

    # ─── Operaciones de escritura ────────────────────────────────────────────

    def ensure_indexes(self):
        """Crea índices útiles para la sincronización y evita duplicados."""
        if self._collection is None:
            return
        try:
            self._collection.create_index(
                [("_id_api", ASCENDING)],
                name="ux_id_api",
                unique=True,
                background=True,
            )
        except OperationFailure:
            self._collection.create_index(
                [("_id_api", ASCENDING)],
                name="idx_id_api",
                background=True,
            )

    def upsert_many(self, records, key_field="_id_api", batch_size=1000):
        """
        Inserta o actualiza múltiples documentos en la colección.
        Trabaja por lotes para evitar cargas muy pesadas en memoria.
        """
        if not records:
            return {"inserted": 0, "modified": 0}

        inserted = 0
        modified = 0

        for start in range(0, len(records), batch_size):
            chunk = records[start:start + batch_size]
            operations = [
                UpdateOne(
                    {key_field: doc[key_field]},
                    {"$set": doc},
                    upsert=True,
                )
                for doc in chunk
                if key_field in doc
            ]

            if not operations:
                continue

            try:
                result = self._collection.bulk_write(operations, ordered=False)
                inserted += result.upserted_count
                modified += result.modified_count
            except BulkWriteError as e:
                print(f"[MongoDAO] Error en bulk_write: {e.details}")

        return {"inserted": inserted, "modified": modified}

    def delete_all(self) -> int:
        """Elimina todos los documentos de la colección."""
        result = self._collection.delete_many({})
        return result.deleted_count

    def delete_stale_records(self, sync_token: str, sync_field: str = "_sync_token") -> int:
        """Elimina registros que no participaron en la última sincronización."""
        result = self._collection.delete_many({sync_field: {"$ne": sync_token}})
        return result.deleted_count

    def save_sync_metadata(self, payload: dict):
        """Guarda metadata de la última sincronización en una colección auxiliar."""
        if self._meta is None:
            return
        doc = {"_id": "etl_status", **payload}
        self._meta.update_one({"_id": "etl_status"}, {"$set": doc}, upsert=True)

    def get_sync_metadata(self) -> dict:
        """Retorna metadata de la última sincronización."""
        if self._meta is None:
            return {}
        return self._meta.find_one({"_id": "etl_status"}, {"_id": 0}) or {}

    # ─── Operaciones de lectura ───────────────────────────────────────────────

    def get_all(self, filters: dict = None, projection: dict = None) -> list:
        """
        Retorna todos los documentos que cumplan los filtros dados.
        Excluye campos internos usados solo por la sincronización.
        """
        query = filters or {}
        proj = projection or {"_id": 0, "_sync_token": 0}
        cursor = self._collection.find(query, proj)
        return list(cursor)

    def get_count(self, filters: dict = None) -> int:
        """Retorna el total de documentos que cumplen el filtro."""
        query = filters or {}
        return self._collection.count_documents(query)

    def get_distinct_values(self, field: str) -> list:
        """Retorna los valores únicos no vacíos de un campo."""
        values = self._collection.distinct(field)
        return sorted([value for value in values if value not in (None, "")])

    def get_collection_info(self) -> dict:
        """Retorna metadata de la colección (nombre, total docs, campos)."""
        total = self.get_count()
        sample = self._collection.find_one({}, {"_id": 0, "_sync_token": 0}) or {}
        return {
            "db_name": self._db.name,
            "collection_name": self._collection.name,
            "total_documents": total,
            "fields": list(sample.keys()),
        }

    def get_sample(self, n: int = 10) -> list:
        """Retorna una muestra aleatoria de N documentos."""
        pipeline = [{"$sample": {"size": n}}, {"$project": {"_id": 0, "_sync_token": 0}}]
        return list(self._collection.aggregate(pipeline))
