from walnut.converters import IORunInfo
from walnut.readers import Reader
from walnut.FileIO import FileIO
from walnut import constants, models
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

    @property
    def n_cell(self):
        if not self.exists():
            raise Exception("Run_info has not been written, failed to get n_cell")
        return self.__content.n_cell

    def read(self):
        if not self.exists():
            raise Exception("No data to read")

        self.__content = self.__file.read()

    def get_species(self) -> constants.SPECIES_LIST:
        return self.__content.species

    def get_content(self) -> models.RunInfo:
        return self.__content.copy()

    def write(self):
        self.__file.write(self.__content)