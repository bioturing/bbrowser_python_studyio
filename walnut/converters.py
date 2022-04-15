from typing import TypeVar, Generic, Any
from abc import ABC, abstractmethod
import json

from walnut.models import Category, Metalist, GeneCollections

OUT_TYPE = TypeVar("OUT_TYPE")

class IOConverter(ABC, Generic[OUT_TYPE]):
    @staticmethod
    @abstractmethod
    def from_str(s: Any) -> OUT_TYPE:
        pass

    @staticmethod
    @abstractmethod
    def to_str(content: OUT_TYPE) -> Any:
        pass

class IOAsIs(IOConverter[OUT_TYPE]):
    @staticmethod
    def from_str(s: OUT_TYPE) -> OUT_TYPE:
        return s
    
    @staticmethod
    def to_str(content: OUT_TYPE) -> OUT_TYPE:
        return content

class IOJSON(IOConverter[dict]):
    @staticmethod
    def from_str(s: str) -> dict:
        return json.loads(s)

    @staticmethod
    def to_str(content: dict) -> str:
        return json.dumps(content)

class IOCategory(IOConverter[Category]):
    @staticmethod
    def from_str(s: str) -> Category:
        content = json.loads(s)
        if isinstance(content, dict):
            return Category.parse_obj(content)
        else:
            return Category(clusters=content)

    @staticmethod
    def to_str(content: Category) -> str:
        return content.json()

class IOMetalist(IOConverter[Metalist]):
    @staticmethod
    def from_str(s: str) -> Metalist:
        obj = json.loads(s)
        if "content" not in obj:
            obj = {"content": obj}
        return Metalist.parse_obj(obj)

    @staticmethod
    def to_str(content: Metalist) -> str:
        return content.json()

class IOGallery(IOConverter[GeneCollections]):
    @staticmethod
    def from_str(s: str) -> GeneCollections:
        return GeneCollections(__root__=json.loads(s))

    @staticmethod
    def to_str(content: GeneCollections) -> str:
        return content.json()