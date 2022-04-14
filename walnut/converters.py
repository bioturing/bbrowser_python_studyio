from typing import TypeVar, Generic
from abc import ABC, abstractmethod
import json

from walnut.models import Category, Metalist

T = TypeVar("T")

class IOConverter(ABC, Generic[T]):
    @staticmethod
    @abstractmethod
    def from_str(s: str) -> T:
        pass

    @staticmethod
    @abstractmethod
    def to_str(content: T) -> str:
        pass


class IOText(IOConverter[str]):
    @staticmethod
    def from_str(s: str) -> str:
        return s

    @staticmethod
    def to_str(content: str) -> str:
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
