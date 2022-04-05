import json
import os
import time
from uuid import uuid4
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic

FileContent = TypeVar("FileContent")

class FileIO(ABC, Generic[FileContent]):
    def __init__(self, filepath: str):
        self.path = filepath

    def exists(self) -> bool:
        return os.path.isfile(self.path)

    @abstractmethod
    def read(self) -> FileContent:
        pass

    @abstractmethod
    def write(self, content: FileContent) -> None:
        pass

class TextFile(FileIO[str]):
    def read(self) -> str:
        with open(self.path) as fopen:
            return fopen.read()

    def write(self, text: str):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w") as fopen:
            fopen.write(text)

class JSONFile(FileIO[dict]):
    def __init__(self, filepath: str, CustomTextFile: Type[TextFile]):
        super().__init__(filepath)
        self.__file = CustomTextFile(filepath)

    def read(self) -> dict:
        json_str = self.__file.read()
        return json.loads(json_str)

    def write(self, obj: dict):
        json_str = json.dumps(obj)
        self.__file.write(json_str)

class FuzzyDict(dict):
    """A dictionary where value can be obtained with multiple keys"""
    def get(self, *keys, default=None):
        for key in keys:
            val = super().get(key)
            if not val is None:
                return val
        return default

    def __len__(self):
        return len(self.keys())

def get_timestamp():
    return time.time() * 1000

def create_uuid():
    return str(uuid4()).replace("-", "")