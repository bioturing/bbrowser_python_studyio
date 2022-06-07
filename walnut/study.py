import os
from typing import List, Optional, Union
from walnut.readers import Reader
from walnut.metadata import Metadata
from walnut.dimred import Dimred
from walnut.gallery import Gallery
from walnut.expression import Expression
from walnut.run_info import RunInfo
from walnut.readers import TextReader
from walnut.gene_db import StudyGeneDB
from walnut.common import create_uuid
from walnut import constants, graphcluster
from scipy import sparse
# from walnut.FileIO import FileIO
import numpy as np
import pandas as pd
import h5py

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
        self.h5pca = os.path.join(self.main_dir, "pca_result.hdf5")
        self.gene_db = os.path.join(self.main_dir, "gene")
        self.sub = os.path.join(self.path, "sub")

class Study:
    def __init__(self, study_folder, species: Union[constants.SPECIES_LIST, None]=None, reader: Reader = TextReader()):
        self.__location = StudyStructure(study_folder)
        self.metadata = Metadata(self.__location.metadata, reader)
        self.expression = Expression(self.__location.h5matrix)
        self.run_info = RunInfo(self.__location.run_info, reader)
        self.dimred = Dimred(self.__location.dimred, TextReader())
        self.gallery = Gallery(self.__location.main_dir, TextReader()) # Gallery is not encrypted

        # If the study exists, ensure gene_db is loaded so that other APIs
        # for genes can be converted correctly
        if self.exists():
            self.run_info.read()

            self.gene_db = StudyGeneDB(self.__location.gene_db, self.run_info.get_species())

            # Old studies will not have .db file for genes. If gene_db
            # does not exists, creates one from the row names of count matrix
            if not self.gene_db.exists():
                self.gene_db.create(self.expression.features)

        else:
            if species is None:
                raise ValueError('If you are creating a new study, please explicitly pass in `species` argument %s' % constants.SPECIES_LIST)
            self.gene_db = StudyGeneDB(self.__location.gene_db, species)

    @property
    def n_cell(self):
        return self.run_info.n_cell

    def exists(self) -> bool:
        return self.run_info.exists() and self.expression.exists

    def create_gene_collection(self, name: str, gene_name: List[str]) -> str:
        """Create a gene collection given a list of genes"""
        if not self.gene_db.is_id(gene_name): # convert name to ID
            gene_name = self.gene_db.convert(gene_name)
        col_id = self.gallery.create_empty_collection(name)
        for gene in gene_name:
            self.gallery.add_item(col_id, gene, [gene])
        self.gallery.write()
        return col_id

    def write_expression_data(self, raw_matrix: Union[sparse.csc_matrix, sparse.csr_matrix],
                              barcodes: List[str],
                              features: List[str],
                              norm_matrix: Union[sparse.csc_matrix, sparse.csr_matrix]=None,
                              feature_type: List[str]=None):

        if self.exists():
          print("WARNING: This study already exists, cannot alter expression data")
          return False

        if self.gene_db.exists():
          print("WARNING: Gene DB for this study already exists, prevent adding and writing new data")
          return False


        if not len(set(barcodes)) == len(barcodes):
            print("WARNING: Please ensure `barcodes` contain no duplicates")
            return False

        raw_features = features.copy()
        self.gene_db.create(raw_features)

        gene_ids = self.gene_db.convert(raw_features)
        self.expression.add_expression_data(raw_matrix=raw_matrix,
                                            barcodes=barcodes,
                                            features=gene_ids,
                                            norm_matrix=norm_matrix,
                                            feature_type=feature_type)
        return self.expression.write()


    def add_dimred(self, coords: np.ndarray, name: str, id: Optional[str]=None) -> str:
        """Add new dimred and return id of successfully added dimred"""
        if id is None:
          id = create_uuid()
        if isinstance(coords, np.ndarray):
          coords_list = coords.tolist()
        elif isinstance(coords, pd.DataFrame):
          coords_list = coords.to_numpy().tolist()
        else:
          raise ValueError('coords must be of type pandas.DataFrame or numpy.ndarray')

        size = list(coords.shape)

        dimred_id = self.dimred.add({'name': name,
                                     'id': id,
                                     'coords': coords_list,
                                     'size': size
                                    })   # type: ignore
        self.dimred.write()

        return dimred_id

    def remove_dimred(self, dimred_id: str):
        return self.dimred.remove(dimred_id)

    def add_metadata(self, name: str, value: List, subcluster_id="root", **kwargs) -> str:
        if subcluster_id != "root":
            graph_cluster = graphcluster.GraphCluster(subcluster_id, self.__location.sub, TextReader())
            selected_arr = graph_cluster.full_selected_array

            filled_category = np.repeat(constants.BIOTURING_UNASSIGNED, self.n_cell)
            for sub_i, main_i in enumerate(selected_arr):  # type: ignore
                filled_category[main_i] = value[sub_i]

            meta_id = self.metadata.add_category(name, filled_category, **kwargs)
        else:
            meta_id = self.metadata.add_category(name, value, **kwargs)

        self.metadata.write_content_by_id(meta_id)
        self.metadata.write_metalist()

        return meta_id

    def get_expression(self, subcluster_id="root", type: constants.UNIT_TYPE_LIST="raw") -> np.ndarray:
        if type == "raw":
            mtx = self.expression.raw_matrix
        else:
            mtx = self.expression.norm_matrix

        if mtx is None:
            print("WARNING: No expression data found, returning empty array")
            return np.array([])

        graph_cluster = graphcluster.GraphCluster(subcluster_id, self.__location.sub, reader=TextReader())
        idx = graph_cluster.full_selected_array
        return mtx[:, idx]

    def get_pca_result(self, subcluster_id="root", batch_correction: constants.BATCH_CORRECTION="none") -> np.ndarray:
        """
        Returning pca_result in cells-by-PCs matrix
        """
        # Creating new study_structure instance to avoid conflicting after `set_root`
        study_structure = StudyStructure(self.__location.path)
        study_structure.set_root(subcluster_id)
        pca_path = study_structure.h5pca

        empty_array = np.array([])

        if not os.path.isfile(pca_path):
            print("No pca_result.hdf5 found at", pca_path)
            return empty_array

        h5pca = h5py.File(pca_path)

        if batch_correction == "none":
            slot = "pca"
        else:
            slot = batch_correction

        pca_result = h5pca.get(slot)
        if pca_result is None:
            print("No pca result found in `%s`" % slot)
            return empty_array
        return pca_result[()].T
