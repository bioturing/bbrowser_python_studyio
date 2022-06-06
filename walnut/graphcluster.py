from walnut.models import GraphClusterDetail
from walnut.FileIO import FileIO
from walnut.converters import IOGraphClusterDetail
import os
from typing import List

class GraphCluster:
    def __init__(self, subcluster_id, sub_folder, reader):
        self.__dir = sub_folder
        self.__file_reader = reader
        self.__info: GraphClusterDetail
        self.__subcluster_id = subcluster_id
        self.read()

    def read(self) -> None:
        if self.__subcluster_id != 'root':
            self.__info = self.__read_cluster_info().read()

    def __get_cluster_info_path(self) -> str:
        return os.path.join(self.__dir, self.__subcluster_id, "cluster_info.json")

    def __read_cluster_info(self) -> FileIO[GraphClusterDetail]:
        return FileIO[GraphClusterDetail](self.__get_cluster_info_path(),
                                            reader=self.__file_reader,
                                            converter=IOGraphClusterDetail)

    def convert_to_main_cluster(self, indices:List[int]) -> List[int]:
        """
        Input:
            indices: selected indices in sub-cluster
        Output:
            selected indices in main cluster
        """
        if self.__subcluster_id == 'root':
            return indices
        selected_arr = self.__info.selectedArr
        return list(map(lambda idx: selected_arr[idx], indices))

    @property
    def full_selected_array(self):
        """
        Return index of all cells within given subcluster_id
        Could be used to subset expression matrix

        Example:
        mtx = study.expression.raw_matrix # Get expression matrix for entire study

        study_structure = StudyStructure(study_dir)
        graph_cluster = graphcluster.GraphCluster(subcluster_id, study_structure.sub, readers.TextReader())

        # Get index for subcluster_id
        idx = graph_cluster.full_selected_array
        # Get expression values for given subcluster
        sub_mtx = mtx[:, idx]
        """

        if self.__subcluster_id == 'root':
            return slice(0, None) # Get everything
        return self.__info.selectedArr
