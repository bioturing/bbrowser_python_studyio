import os
from walnut.common import FileIO, JSONFile

class Gallery:
    def __init__(self, gallery_folder, TextFile: FileIO):
        self.__dir = gallery_folder
        self.__TextFile = TextFile
        self.__old_gallery = JSONFile(os.path.join(self.__dir, "gene_gallery.json"), self.__TextFile)
        self.__gallery = JSONFile(os.path.join(self.__dir, "gene_gallery_2.json"), self.__TextFile)
    
    # TODO: needs more APIs