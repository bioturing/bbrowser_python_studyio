import os
import pandas as pd
from walnut import common
from typing import List
import numpy as np
from walnut.converters import IOAsIs
from walnut.FileIO import FileIO
from walnut.readers import SQLReader

class GeneDB:
    def __init__(self, gene_db_dir, species):
        self.__file = FileIO[pd.DataFrame](os.path.join(gene_db_dir, '%s.db' % species), SQLReader(), IOAsIs)
        self.__df = pd.DataFrame(columns=["gene_id", "name", "primary"])
    
    def exists(self):
        return self.__file.exists()
    
    def read(self):
        if not self.exists():
            raise Exception("No data to read")
        
        self.__df = self.__file.read()
    
    def write(self):
        if self.__df.index.size == 0:
            raise Exception("Cannot write empty data")
        self.__file.write(self.__df)

    def convert(self, names: List[str], _from: str="name", _to: str="gene_id") -> List[str]:
        """Convert a list of genes to symbols or IDs"""
        ids = []
        prim = self.__df[self.__df["primary"] == 1]
        alias = self.__df[self.__df["primary"] == 0]
        mapping = {}

        for _, item in prim.iterrows():
            if not item[_from] in mapping:
                mapping[item[_from]] = item[_to]
        
        for _, item in alias.iterrows():
            if not item[_from] in mapping:
                mapping[item[_from]] = item[_to]

        for name in names:
            ids.append(mapping.get(name, name))
        return ids
    
    def is_id(self, ids: List[str]) -> bool:
        pre_in = [x[: 4] for x in ids]
        pre_ref = np.unique([x[: 4] for x in self.__df["gene_id"]])
        valid = np.sum(np.isin(pre_in, pre_ref))
        prc_valid = valid * 100 / len(ids)
        return prc_valid > 50
    
    def to_df(self) -> pd.DataFrame:
        return self.__df.copy()
    
    def from_df(self, df: pd.DataFrame):
        self.__df = df.copy()

class StudyGeneDB(GeneDB):
    def __init__(self, gene_db_dir, species):
        super().__init__(gene_db_dir, species)
        self.__ref = GeneDB(common.get_pkg_data(), species)
        self.__ref.read()

    def create(self, gene_id: List[str], gene_name: List[str]=None):
        """
        Create gene DB for a study given a list of genes (usually from matrix.hdf5)
        This will make sure gene_id are unique
        If only gene name are available, convert to gene id based on current reference.
        Following conversion, if duplicates are found in the resulting gene ids,
        the corresponding original gene names will be kept
        Argument:
        - gene_id: list of gene id, no duplicates allowed
        - gene_name: List of corresponding gene name.
        If both are provided, gene_db will be written as is.
        If only one list is available, always pass to `gene_id` argument
        """

        if not len(set(gene_id)) == len(gene_id):
            raise ValueError("Please make sure `gene_id` contains no duplicates")

        if not gene_name:
            if self.__ref.is_id(gene_id):
                gene_name = self.__ref.convert(gene_id, _from="gene_id", _to="name")
            else:
                gene_name = gene_id
                gene_id = self.__ref.convert(gene_id)
                gene_id = self.check_duplicate(gene_id, gene_name)
        else:
            assert len(gene_id) == len(gene_name)


        df = pd.DataFrame({"gene_id": gene_id, "name": gene_name, "primary": 1})
        self.from_df(df)
        self.write()
    
    def convert(self, names: List[str], _from: str="name", _to: str="gene_id", use_ref: bool=False) -> List[str]:
        if (not use_ref) and self.exists():
            return super().convert(names, _from, _to)
        else:
            return self.__ref.convert(names, _from, _to)
    
    def is_id(self, ids: List[str], use_ref: bool=False) -> bool:
        if (not use_ref) and self.exists():
            return super().is_id(ids)
        else:
            return self.__ref.is_id(ids)
    
    @staticmethod
    def check_duplicate(gene_ids: List[str], gene_names: List[str]):
        """
        Given two equal-length lists, check if item in `ids` contain duplicates.
        If yes, replaced with corresponding item in `names`.
        """
        
        if len(set(gene_ids)) == len(gene_ids):
            return gene_ids
        
        if len(set(gene_names)) != len(gene_names):
            raise ValueError("`names` must contain no duplicates")
        gene_ids = pd.Series(gene_ids)
        gene_names = pd.Series(gene_names)
        dup_idx = gene_ids.duplicated()
        duplicates = gene_ids[dup_idx]
        
        print("Reverting %s ID(s) to origin(s) due to duplicates:" % len(duplicates))
        print("- ID:", duplicates)
        print("- Origin:", gene_names[dup_idx])

        for dup in duplicates:
            idx = gene_ids == dup
            gene_ids[idx] = gene_names[idx]

        if sum(gene_ids.duplicated()) > 0:
            raise ValueError("Something went wrong while trying to ensuring uniqueness of gene ids")

        return gene_ids.values.tolist()
            

    def make_unique(items: List[str]):
        if len(set(items)) == len(items):
            return items
    
        items = pd.Series(items)
        duplicates = items[items.duplicated()]
        
        print('Found %s duplicates' % len(duplicates))

        for dup in duplicates:
            dup_idx = items[items == dup].index

            for i, j in enumerate(dup_idx[1:]):
                items[j] = items[j] + '.' + str(i+1)

        assert sum(items.duplicated()) == 0
        return items.values.tolist()