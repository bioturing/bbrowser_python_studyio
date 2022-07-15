import os
import json
from pydantic import BaseModel
from typing import Dict, List, Optional
import sqlite3
import pandas as pd
from walnut.common import get_timestamp
from walnut.readers import TextReader


class SpotCellTypes(BaseModel):
    __root__: Dict[str, List[float]]

class CellTypeCoordinates(BaseModel):
    x: List[float]
    y: List[float]
    cell_type: List[int]
    frequency: List[float]

class DeconvolutionResult(BaseModel):
    """
    Data model for actual result of a deconvolution analysis
    """
    spot_celltypes: SpotCellTypes
    celltype_names: Dict[str, str]
    celltypes: Dict[str, List[float]]
    gene_ids: List[str]
    celltype_coordinates: CellTypeCoordinates
    log2_fc: Dict[str, List[float]]
    image_data: Optional[str]
    colors: Optional[List[str]]
    n_topics: Optional[int]

class DeconvolutionMetaInfo(BaseModel):
    """
    Data model for meta info of a deconvolution analysis
    """
    id: str
    n_topics: int
    params: str

class DeconvolutionResultHandler:
    def __init__(self, deconvolution_folder: str) -> None:
        self.__dir = deconvolution_folder
        self.db_path = os.path.join(self.__dir, 'deconvolution_result.db')
        self.table_key = 'deconvolution_result'
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.__create_table()

        self.read()


    @property
    def exists(self):
        return os.path.isfile(self.db_path)


    def __create_table(self):
        with sqlite3.connect(self.db_path) as con:
            cursor = con.cursor()
            sql = f'''CREATE TABLE IF NOT EXISTS {self.table_key}(
                ID CHAR PRIMARY KEY NOT NULL,
                DATE FLOAT,
                N_TOPICS INT,
                PARAMS TEXT
                )
                '''
            cursor.execute(sql)
            con.commit()


    def read(self):
        with sqlite3.connect(self.db_path) as con:
            df = pd.read_sql_query(f"SELECT * FROM {self.table_key}", con, index_col="ID")
        self.df = df


    def get_available_results(self):
        return self.df.to_dict()


    @property
    def keys(self):
        return self.df.index


    def get(self, id: str):
        path = self.__get_result_path(id)
        reader = TextReader()
        return json.loads(reader.read(path))


    def add_new_result(self, meta_info: DeconvolutionMetaInfo, result: DeconvolutionResult):

        self.write(meta_info.id, result)

        with sqlite3.connect(self.db_path) as con:
            cursor = con.cursor()
            cursor.execute(f'''INSERT INTO {self.table_key}
                (ID, DATE, N_TOPICS, PARAMS)
                VALUES (?, ?, ?, ?)
                ''', (meta_info.id, get_timestamp(), meta_info.n_topics, meta_info.params))
            con.commit()

        self.read()

    def read_file(self, file_path: str):
        fopen = open(file_path, 'r')
        data = json.loads(fopen.read())
        fopen.close()

        return data

    def __get_result_path(self, id) -> str:
        return os.path.join(self.__dir, id)

    def write(self, result_id: str, info: DeconvolutionResult):
        reader = TextReader()
        reader.write(info.json(), self.__get_result_path(result_id))
