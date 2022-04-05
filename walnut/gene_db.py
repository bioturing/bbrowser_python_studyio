import os
import sqlite3
import pandas as pd
from walnut import common
from typing import List
import numpy as np

class GeneTableSQL(common.FileIO):
    def read(self) -> pd.DataFrame:
        with sqlite3.connect(self.path) as con:
            df = pd.read_sql_query("SELECT * FROM gene_name", con)
        return df
    
    def write(self, df: pd.DataFrame):
        with sqlite3.connect(self.path) as con:
            df.to_sql("gene_name", con)

class GeneDB:
    def __init__(self, gene_db_dir, species):
        self.__file = GeneTableSQL(os.path.join(gene_db_dir, '%s.db' % species))
        self.__df = pd.DataFrame(columns=["gene_id", "gene_name", "primary"])
    
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
            