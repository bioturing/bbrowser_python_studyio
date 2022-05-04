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
    gene: Tuple[int, int] = (0, 0)
    mito: int = 100
    top: int = 2000

    @validator("gene", pre=True)
    def fix_weird_gene_values(cls, v, values):
      if not isinstance(v, list) or len(v) < 2:
        print("WARNING: Invalid FilterSetting found", v)
        return (0,0) # Fix gene = [0]
      
      for i, item in enumerate(v):
        if isinstance(item, list):
          print("WARNING: Invalid FilterSetting found", v)
          v[i] = int(item[0]) # Fix gene = [[200], [0]] --> [200, 0]
      return v


class AnaSetting(BaseModel):
    inputType: List[constants.INPUT_FORMAT_LIST] = ["mtx"]
    normMethod: constants.NORMALIZATION_LIST = "lognorm"
    filter: FilterSetting = FilterSetting()

    @validator("inputType", pre=True)
    def check_input_type(cls, v):
      if not isinstance(v, list):
        v = [v] # Fix "bcs" -> ["bcs"]
      for i, item in enumerate(v):
        v[i] = v[i].lower() # backward compatibility
      return v

class RunInfo(BaseModel):
    hash_id: str
    title: str
    n_cell: int
    species: constants.SPECIES_LIST = "human"
    omics: List[constants.OMICS_LIST] = ["RNA"]
    unit_settings: UnitSettings = UnitSettings()
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
    n_batch: Optional[int] = 1
    version: Optional[int] = 16

    @validator("version", always=True)
    def set_version(cls, _):
        return 16

    @validator("n_batch", always=True)
    def set_n_batch(cls, _, values):
        return len(values["ana_setting"].inputType)
    
    @validator("unit_settings", pre=True)
    def set_unit_settings(cls, value):
        settings = {}
        for omic in constants.OMICS_LIST.__args__:  # type: ignore
            settings[omic] = OmicUnitSettings.parse_obj(
                value.get(omic, {"type": "raw" if omic == "PRTB" else "norm", "transform": "none"})
            )
        return UnitSettings.parse_obj(settings)