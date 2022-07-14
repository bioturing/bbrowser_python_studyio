import os
import json
from pydantic import BaseModel
from typing import Dict, List, Optional
import sqlite3
import pandas as pd
from walnut.common import get_timestamp
from walnut.readers import TextReader


class DeconvolutionArgs(BaseModel):
    class Config:
        validate_assignment = True

    study_dir: str
    """
    path to study
    """
    subcluster_id: str = "root"
    """
    id of a sub cluster (root if it is main cluster)
    """
    n_top_genes: int = 1000
    """
    number of highly-variable genes to keep
    """
    min_genes: int = 0
    """
    minimum number of genes required for a cell
    """
    min_cells: int = 0
    """
    minimum number of cells expressed required for a gene
    """
    max_cells: int = None
    """
    maximum number of cells expressed required for a gene
    """
    min_celltypes: int
    max_celltypes: int
    """
    range of toptics to train
    """
    image_path: Optional[str]
    """
    path to image to draw pie
    """
    output_path: str
    """
    output path to write result
    """
    result_id: str
    """
    output path to write result
    """
    legend: bool = False
    """
    include legend in image or not
    """
    random_state: int = 2409

class SpotCellTypes(BaseModel):
    __root__: Dict[str, List[float]]

class CellTypeCoordinates(BaseModel):
    x: List[float]
    y: List[float]
    cell_type: List[int]
    frequency: List[float]

class DeconvolutionInfo(BaseModel):
    spot_celltypes: SpotCellTypes
    celltype_names: Dict[str, str]
    celltypes: Dict[str, List[float]]
    gene_ids: List[str]
    celltype_coordinates: CellTypeCoordinates
    log2_fc: Dict[str, List[float]]
    image_data: Optional[str]
    colors: Optional[List[str]]
    n_topics: Optional[int]
    params: Optional[DeconvolutionArgs]

class DeconvolutionResult:
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
                N_TOPICS INT
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


    def add_new_result(self, info: dict):

        self.write(info['id'], info['result'])

        with sqlite3.connect(self.db_path) as con:
            cursor = con.cursor()
            cursor.execute(f'''INSERT INTO {self.table_key}
                (ID, DATE, N_TOPICS)
                VALUES (?, ?, ?)
                ''', (info['id'], get_timestamp(), info['n_topics']))
            con.commit()

        self.read()

    def read_file(self, file_path: str):
        fopen = open(file_path, 'r')
        data = json.loads(fopen.read())
        fopen.close()

        return data

    def __get_result_path(self, id) -> str:
        return os.path.join(self.__dir, id)

    def write(self, result_id: str, info: DeconvolutionInfo):
        reader = TextReader()
        reader.write(info.json(), self.__get_result_path(result_id))
