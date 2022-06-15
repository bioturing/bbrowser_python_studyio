import os
from walnut.FileIO import FileIO
from walnut.readers import Reader, TextReader
from walnut.models import DeconvolutionInfo
from walnut.converters import IODeconvolution

class DeconvolutionResult:
    def __init__(self, deconvolution_folder: str, reader: Reader = TextReader()) -> None:
        self.__dir = deconvolution_folder
        self.__reader = reader

    def get_result_path(self, id) -> str:
        return os.path.join(self.__dir, id)

    def get_result_io(self, result_id: str) -> FileIO:
        return FileIO(self.get_result_path(result_id), self.__reader, IODeconvolution)

    def exists(self, result_id: str) -> bool:
        return self.get_result_io(result_id).exists()

    def get(self, result_id: str) -> DeconvolutionInfo:
        if not self.exists(result_id): 
            print("WARNING: No deconvolution result to read")
            return False
        
        return self.get_result_io(result_id).read()

    def write(self, result_id: str, info: DeconvolutionInfo):
        self.get_result_io(result_id).write(info)
        
        return True