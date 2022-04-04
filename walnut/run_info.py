from pydantic import BaseModel
from typing import Tuple, List
from walnut import constants
from walnut.common import FileIO
from enum import Enum

class UnitSettings(BaseModel):
    type: constants.UNIT_TYPE_LIST
    transform: constants.UNIT_TRANSFORM_LIST

class Commit(BaseModel):
    description: str
    hash_id: str
    created_by: str
    created_at: constants.NUM

class FilterSetting(BaseModel):
    cell: int
    gene: Tuple[int, int]
    mito: int
    top: int

class AnaSetting(BaseModel):
    inputType: List[constants.INPUT_FORMAT_LIST]
    normMethod: constants.NORMALIZATION_LIST
    filter: FilterSetting

class RunInfoStr(BaseModel):
    hash_id: str
    title: str
    species: constants.SPECIES_LIST
    n_cell: int
    omics: List[constants.OMICS_LIST]
    unit_settings: dict[constants.OMICS_LIST, UnitSettings]
    modified_date: constants.NUM
    misc: dict[str, str]
    papers: List[str]
    abstract: str
    author: list[str]
    unit: constants.UNIT_LIST
    shareTag: list[str]
    tag: list[str]
    history: list[Commit]
    is_public: bool
    ana_setting: AnaSetting
    version: int

class RunInfo():
    def __init__(self, filepath, TextFile: FileIO):
        self.__file = TextFile(filepath)
    
    # TODO: needs more APIs