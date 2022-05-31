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
from walnut import constants
from scipy import sparse
import numpy as np
import pandas as pd

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
        self.gene_db = os.path.join(self.main_dir, "gene")

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
                                    })
        self.dimred.write()

        return dimred_id

    def remove_dimred(self, dimred_id: str):
        return self.dimred.remove(dimred_id)