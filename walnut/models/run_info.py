from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel, validator
from walnut import constants, common

class OmicUnitSettings(BaseModel):
    type: constants.UNIT_TYPE_LIST
    transform: constants.UNIT_TRANSFORM_LIST = "none"

class UnitSettings(BaseModel):
    RNA: OmicUnitSettings = OmicUnitSettings(type="norm", transform="none")
    ADT: OmicUnitSettings = OmicUnitSettings(type="norm", transform="none")
    PRTB: OmicUnitSettings = OmicUnitSettings(type="raw", transform="none")

class FilterSetting(BaseModel):
    cell: int = 0
    gene: Tuple[int, int] = [0, 0]
    mito: int = 100
    top: int = 2000

class AnaSetting(BaseModel):
    inputType: List[constants.INPUT_FORMAT_LIST] = ["mtx"]
    normMethod: constants.NORMALIZATION_LIST = "lognorm"
    filter: FilterSetting = FilterSetting()

class RunInfo(BaseModel):
    hash_id: str
    title: str
    n_cell: int
    species: constants.SPECIES_LIST = "human"
    omics: List[constants.OMICS_LIST] = ["RNA"]
    unit_settings: Dict[constants.OMICS_LIST, UnitSettings] = UnitSettings()
    modified_date: constants.NUM = common.get_timestamp()
    misc: Dict[str, str] = {}
    papers: List[str] = []
    abstract: str = ''
    author: List[str] = []
    unit: constants.UNIT_LIST = "umi"
    shareTag: List[str] = []
    tag: List[str] = []
    history: List[common.History] = [common.create_history()]
    is_public: bool = True
    ana_setting: AnaSetting = AnaSetting()
    n_batch: Optional[int]
    version: Optional[int]

    @validator("version", always=True)
    def set_version(cls, _):
        return 16

    @validator("n_batch", always=True)
    def set_vn_batch(cls, _, values):
        return len(values["ana_setting"].inputType)