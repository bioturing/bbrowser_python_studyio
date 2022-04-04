import os
from walnut.common import FileIO, JSONFile

class Dimred:
    def __init__(self, dimred_folder, TextFile: FileIO):
        self.__dir = dimred_folder
        self.__TextFile = TextFile
        self.__metalist = JSONFile(os.path.join(self.__dir, "meta"), self.__TextFile)
    
    # TODO: needs more APIs