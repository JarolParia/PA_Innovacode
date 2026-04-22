"""
dao/mongo_dao.py
----------------
Capa de acceso a datos (DAO) para MongoDB.
Toda interacción con la base de datos pasa por esta clase.
"""

from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure, BulkWriteError
import os
from dotenv import load_dotenv

load_dotenv()


class MongoDAO:
    """Gestiona la conexión y operaciones CRUD sobre MongoDB."""

    def __init__(self):
        self._client = None
        self._db = None
        self._collection = None

    def connect(self):
        """Establece conexión con MongoDB usando variables de entorno."""
        uri = os.getenv("MONGO_URI")
        db_name = os.getenv("DB_NAME", "matriculas_antioquia")
        collection_name = os.getenv("COLLECTION_NAME", "estudiantes")

        if not uri:
            raise ValueError("MONGO_URI no está definida en las variables de entorno.")

        self._client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Verifica que la conexión sea exitosa
        self._client.admin.command("ping")
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]

    def disconnect(self):
        """Cierra la conexión con MongoDB."""
        if self._client:
            self._client.close()
            self._client = None

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

    def upsert_many(self, records: list[dict], key_field: str = "_id_api") -> dict:
        """
        Inserta o actualiza múltiples documentos en la colección.

        Args:
            records: Lista de documentos a insertar/actualizar.
            key_field: Campo usado como clave única para el upsert.

        Returns:
            Diccionario con conteo de insertados y modificados.
        """
        if not records:
            return {"inserted": 0, "modified": 0}

        operations = [
            UpdateOne(
                {key_field: doc[key_field]},
                {"$set": doc},
                upsert=True
            )
            for doc in records
            if key_field in doc
        ]

        try:
            result = self._collection.bulk_write(operations, ordered=False)
            return {
                "inserted": result.upserted_count,
                "modified": result.modified_count,
            }
        except BulkWriteError as e:
            print(f"[MongoDAO] Error en bulk_write: {e.details}")
            return {"inserted": 0, "modified": 0}

    # ─── Operaciones de lectura ───────────────────────────────────────────────

    def get_all(self, filters: dict = None, projection: dict = None) -> list[dict]:
        """
        Retorna todos los documentos que cumplan los filtros dados.

        Args:
            filters: Diccionario de filtros MongoDB (ej. {"genero": "HOMBRE"}).
            projection: Campos a incluir/excluir (ej. {"_id": 0}).

        Returns:
            Lista de documentos.
        """
        query = filters or {}
        proj = projection or {"_id": 0}
        cursor = self._collection.find(query, proj)
        return list(cursor)

    def get_count(self, filters: dict = None) -> int:
        """Retorna el total de documentos que cumplen el filtro."""
        query = filters or {}
        return self._collection.count_documents(query)

    def get_distinct_values(self, field: str) -> list:
        """Retorna los valores únicos de un campo."""
        return sorted(self._collection.distinct(field))

    def get_collection_info(self) -> dict:
        """Retorna metadata de la colección (nombre, total docs, campos)."""
        total = self.get_count()
        sample = self._collection.find_one({}, {"_id": 0}) or {}
        return {
            "db_name": self._db.name,
            "collection_name": self._collection.name,
            "total_documents": total,
            "fields": list(sample.keys()),
        }

    def get_sample(self, n: int = 10) -> list[dict]:
        """Retorna una muestra aleatoria de N documentos."""
        pipeline = [{"$sample": {"size": n}}, {"$project": {"_id": 0}}]
        return list(self._collection.aggregate(pipeline))
    

    def delete_all(self) -> int:
        """Elimina todos los documentos de la colección."""
        result = self._collection.delete_many({})
        return result.deleted_count

