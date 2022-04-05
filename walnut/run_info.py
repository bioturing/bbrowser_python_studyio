from typing import Tuple, List, Dict
from walnut import constants
from walnut.common import FileIO

try:
    from typing import TypedDict
except:
    from typing_extensions import TypedDict

class UnitSettings(TypedDict):
    type: constants.UNIT_TYPE_LIST
    transform: constants.UNIT_TRANSFORM_LIST

class Commit(TypedDict):
    description: str
    hash_id: str
    created_by: str
    created_at: constants.NUM

class FilterSetting(TypedDict):
    cell: int
    gene: Tuple[int, int]
    mito: int
    top: int

class AnaSetting(TypedDict):
    inputType: List[constants.INPUT_FORMAT_LIST]
    normMethod: constants.NORMALIZATION_LIST
    filter: FilterSetting

class RunInfoStr(TypedDict):
    hash_id: str
    title: str
    species: constants.SPECIES_LIST
    n_cell: int
    omics: List[constants.OMICS_LIST]
    unit_settings: Dict[constants.OMICS_LIST, UnitSettings]
    modified_date: constants.NUM
    misc: Dict[str, str]
    papers: List[str]
    abstract: str
    author: List[str]
    unit: constants.UNIT_LIST
    shareTag: List[str]
    tag: List[str]
    history: List[Commit]
    is_public: bool
    ana_setting: AnaSetting
    version: int

class RunInfo():
    def __init__(self, filepath, TextFile: FileIO):
        self.__file = TextFile(filepath)
    
    # TODO: needs more APIs