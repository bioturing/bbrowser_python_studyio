from walnut.converters import IORunInfo
from walnut.readers import Reader
from walnut.FileIO import FileIO
from walnut import models
import os

class RunInfo():
    def __init__(self, filepath: str, reader: Reader):
        self.__file = FileIO[models.RunInfo](filepath, reader, IORunInfo)
        self.__content = models.RunInfo(
            hash_id = os.path.basename(os.path.dirname(self.__file.path)),
            title = "Untitled study",
            n_cell = 0,
        )
    
    def exists(self):
        return self.__file.exists()

    def read(self):
        if not self.exists():
            raise Exception("No data to read")

        self.__content = self.__file.read()
    
    def get_content(self) -> models.RunInfo:
        return self.__content.copy()

    def write(self):
        self.__file.write(self.__content)