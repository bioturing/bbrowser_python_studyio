import os
import sqlite3
import pandas as pd
from walnut import common
from typing import List
import numpy as np
from walnut.converters import IOAsIs
from walnut.readers import Reader
from walnut.FileIO import FileIO
import json

class SQLReader(Reader):
    @staticmethod
    def read(filepath: str) -> pd.DataFrame:
        with sqlite3.connect(filepath) as con:
            df = pd.read_sql_query("SELECT * FROM gene_name", con)
        return df
    
    @staticmethod
    def write(df: pd.DataFrame, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with sqlite3.connect(filepath) as con:
            df.to_sql("gene_name", con)

class GeneDB:
    def __init__(self, gene_db_dir, species):
        self.__file = FileIO(os.path.join(gene_db_dir, '%s.db' % species), SQLReader(), IOAsIs)
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
        id_dict = {}
        ids = []
        prim = self.__df[self.__df["primary"] == 1]
        alias = self.__df[self.__df["primary"] == 0]
        for name in names:
            id = id_dict.get(name)
            if id:
                ids.append(id)
                continue

            id = prim[prim[_from] == name][_to]
            if id.size > 0:
                id = id.tolist()[0]
            else:
                id = alias[alias[_from] == name][_to]
                if id.size > 0:
                    id = id.tolist()[0]
                else:
                    id = name
            id_dict[name] = id
            ids.append(id)
        return ids
    
    def is_id(self, ids: List[str]) -> bool:
        pre_in = [x[: 4] for x in ids]
        pre_ref = np.unique([x[: 4] for x in self.__df["gene_id"]])
        valid = np.sum(np.isin(pre_in, pre_ref))
        prc_valid = valid * 100 / len(ids)
        return prc_valid > 50
    
    def to_df(self) -> pd.DataFrame:
        return self.__df
    
    def from_df(self, df: pd.DataFrame):
        self.__df = df

class StudyGeneDB(GeneDB):
    def __init__(self, gene_db_dir, species):
        super().__init__(gene_db_dir, species)
        self.__ref = GeneDB(common.get_pkg_data(), species)

    def create(self, gene_id: List[str], gene_name: List[str]=None):
        """Create gene DB for a study given a list of genes (usually from matrix.hdf5)"""
        if not gene_name:
            self.__ref.read() # Load gene db
            if self.__ref.is_id(gene_id):
                gene_name = self.__ref.convert(gene_id, _from="gene_id", _to="name")
            else:
                gene_name = gene_id
                gene_id = self.__ref.convert(gene_id)

        df = pd.DataFrame({"gene_id": gene_id, "name": gene_name, "primary": 1})
        self.from_df(df)
        self.write()
        