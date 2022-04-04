import json
import os
from abc import ABC, abstractmethod

class FileIO(ABC):
    def __init__(self, filepath):
        self.path = filepath
    
    def exists(self):
        os.path.isfile(self.path)
    
    @abstractmethod
    def read(self) -> str:
        pass

    @abstractmethod
    def write(self, text: str):
        pass

class TextFile(FileIO):
    def read(self) -> str:
        with open(self.path) as fopen:
            return fopen.read()
    
    def write(self, text: str):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w") as fopen:
            fopen.write(text)

class JSONFile(FileIO):
    def __init__(self, filepath: str, CustomTextFile: FileIO):
        super().__init__(filepath)
        self.__file = CustomTextFile(filepath)

    def read(self):
        json_str = self.__file.read()
        return json.loads(json_str)
    
    def write(self, obj):
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
