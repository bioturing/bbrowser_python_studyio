import os

from walnut.common import FileIO, TextFile
from walnut.metadata import Metadata
from walnut.dimred import Dimred
from walnut.gallery import Gallery
from walnut.expression import Expression
from walnut.run_info import RunInfo

class StudyStructure:
    def __init__(self, study_folder):
        self.path = study_folder
        self.run_info = os.path.join(self.path, "run_info.json")
        self.set_root("root")

    def set_root(self, root):
        self.root = root
        self.main_dir = os.path.join(self.path, "main") if self.root == "root" else os.path.join(self.path, "sub", self.root)
        self.metadata = os.path.join(self.path, "main", "metadata")
        self.dimred = os.path.join(self.main_dir, "dimred")
        self.h5matrix = os.path.join(self.path, "main", "matrix.hdf5")

class Study:
    def __init__(self, study_folder, CustomTextFile: FileIO=TextFile):
        self.__location = StudyStructure(study_folder)
        self.__TextFile = CustomTextFile
        #self.metadata = Metadata(self.__location.metadata, self.__TextFile)
        self.expression = Expression(self.__location.h5matrix)
        self.run_info = RunInfo(self.__location.run_info, self.__TextFile)
        self.dimred = Dimred(self.__location.dimred, self.__TextFile)
        self.gallery = Gallery(self.__location.main_dir, self.__TextFile)