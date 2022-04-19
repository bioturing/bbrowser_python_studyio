from abc import ABC
from typing import Generic, TypeVar, Type
import os

from walnut.converters import IOConverter
from walnut.readers import Reader

T = TypeVar("T")

class FileIO(ABC, Generic[T]):
    """
    A class that handles file IO. It takes a path to some file and a :class:`IOConverter[T]` class
    which converts ``str``s into some type ``T``, e.g. ``dict``, ``int``, etc. It provides :func:`FileIO.read`
    and :func:`FileIO.write` to read the content of the file into format ``T``
    and write objects of type ``T`` to the file, using the converter.
    """
    def __init__(self, filepath: str, reader: Reader, converter: Type[IOConverter[T]]):
        self.path = filepath
        self.reader = reader
        self.converter = converter

    def exists(self) -> bool:
        return os.path.isfile(self.path)

    def _read_file(self) -> str:
        return self.reader.read(self.path)

    def read(self) -> T:
        file_content = self._read_file()
        return self.converter.from_str(file_content)

    def _write_file(self, content: str) -> None:
        self.reader.write(content, self.path)

    def delete(self) -> None:
        if self.exists():
            os.remove(self.path)

    def write(self, content: T) -> None:
        self._write_file(self.converter.to_str(content))
