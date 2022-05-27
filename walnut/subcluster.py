from walnut.models import GraphClusterDetail
from walnut.FileIO import FileIO
from walnut.converters import IOGraphClusterDetail
import os
from typing import List
from numbers import Number

class SubCluster:
    def __init__(self, sub_folder, reader):
        self.__dir = sub_folder
        self.__file_reader = reader
        self.__info: GraphClusterDetail = None
        self.read()

    def read(self) -> None:
        self.__info = self.__read_cluster_info().read()

    def __get_cluster_info_path(self) -> str:
        return os.path.join(self.__dir, "cluster_info.json")

    def __read_cluster_info(self) -> FileIO[GraphClusterDetail]:
        return FileIO[GraphClusterDetail](self.__get_cluster_info_path(),
                                            reader=self.__file_reader,
                                            converter=IOGraphClusterDetail)
    
    def get_selected_addr(self) -> List[int]:
        return self.__info.selectedArr

    def convert_to_main_cluster(self, indexes:List[int]) -> List[int]:
        pass

    def convert_to_sub_cluster(self, indexes:List[int]) -> List[int]:
        selected_arr = self.get_selected_addr()
        return list(map(lambda idx: selected_arr[int(idx)] if isinstance(selected_arr[int(idx)], Number) else float('NaN'), indexes))
