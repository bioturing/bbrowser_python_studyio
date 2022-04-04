import os
from walnut.common import FileIO, JSONFile

class Metadata:
    def __init__(self, metadata_folder, TextFile: FileIO):
        self.__dir = metadata_folder
        self.__TextFile = TextFile
        self.__metalist = JSONFile(os.path.join(self.__dir, "metalist.json"), self.__TextFile)
    
    # TODO: needs more APIs