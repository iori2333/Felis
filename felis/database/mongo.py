from typing import TYPE_CHECKING, Generic, Type, TypeVar
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.database import Database
from bson import ObjectId

if TYPE_CHECKING:
    from .database import DatabaseConfig


T = TypeVar("T", bound=BaseModel)


class MongoDatabase:
    def __init__(self, config: "DatabaseConfig") -> None:
        self.client = MongoClient(
            config.mongo_host,
            config.mongo_port,
            username=config.user,
            password=config.password,
        )
        self.db = self.client[config.name]

    def get_collection(self, name: str, original_type: Type[T]) -> "Collection[T]":
        return Collection(name, self.db, original_type)


class Collection(Generic[T]):
    def __init__(self, name: str, db: Database, original_type: Type[T]) -> None:
        self.db = db
        self.name = name
        self.original_type = original_type
        self.collection = self.db[name]

    def save(self, document: T) -> None:
        self.collection.insert_one(document.dict())

    def find_one(self, query: dict) -> T:
        result = self.collection.find_one(query)
        if result is None:
            raise ValueError("No document found")
        return self.original_type.parse_obj(result)

    def find(self, query: dict, limit: int | None = None) -> list[T]:
        cursor = self.collection.find(query)
        if limit is not None:
            cursor = cursor.limit(limit)
        return [self.original_type.parse_obj(result) for result in cursor]

    def get(self, id: ObjectId) -> T | None:
        cursor = self.collection.find_one({"_id": id})
        if cursor is None:
            return None
        return self.original_type.parse_obj(cursor)
