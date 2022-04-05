from typing import Tuple, List, Dict
from walnut import constants, common
import os

try:
    from typing import TypedDict
except:
    from typing_extensions import TypedDict

class UnitSettings(TypedDict):
    type: constants.UNIT_TYPE_LIST
    transform: constants.UNIT_TRANSFORM_LIST

class FilterSetting(TypedDict):
    cell: int
    gene: Tuple[int, int]
    mito: int
    top: int

class AnaSetting(TypedDict):
    inputType: List[constants.INPUT_FORMAT_LIST]
    normMethod: constants.NORMALIZATION_LIST
    filter: FilterSetting

class RunInfoStruc(TypedDict):
    hash_id: str
    title: str
    species: constants.SPECIES_LIST
    n_cell: int
    n_batch: int
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
    history: List[common.Commit]
    is_public: bool
    ana_setting: AnaSetting
    version: int

class RunInfo():
    def __init__(self, filepath, TextFile: common.FileIO):
        self.__file = common.JSONFile(filepath, TextFile)

        now = common.get_timestamp()
        self.__content = RunInfoStruc(
            hash_id = os.path.basename(os.path.dirname(self.__file.path)),
            title = "Untitled study",
            species = "human",
            n_cell = 0,
            n_batch = 1,
            omics = ["RNA"],
            unit_settings = {
                "RNA": UnitSettings(type="norm", transform="none"),
                "ADT": UnitSettings(type="norm", transform="none"),
                "PRTB": UnitSettings(type="raw", transform="none")
            },
            modified_date = now,
            misc = {},
            papers = [],
            abstract = 'No description',
            author = [],
            unit = "umi",
            shareTag = [],
            tag = [],
            history = [common.create_commit()],
            is_public = False,
            ana_setting = AnaSetting(
                inputType = ["mtx"],
                normMethod = "lognorm",
                filter = FilterSetting(cell=0, gene=[0, 0], mito=100, top=2000)
            ),
            version = 16
        )
        self.__content = common.FuzzyDict(self.__content)
    
    def __get_value_optional(self, keys: list[str], content: common.FuzzyDict, _type: type, default=None):
        if not default:
            default = self.__content[keys[0]]
        val = content.get(*keys, default=default)
        if not isinstance(val, _type):
            print("WARN: invalid `%s`" % keys[0])
            val = self.__content[keys[0]]
        return val
    
    def exists(self):
        return self.__file.exists()

    def read(self):
        if not self.exists():
            raise Exception("No data to read")

        content = common.FuzzyDict(self.__file.read())
        hash_id = content.get("hash_id", "study_id", default=self.__content["hash_id"])
        if hash_id != self.__content["hash_id"]:
            raise Exception("Study ID is not consistent with the folder name")        
        species = content.get("index_type", "species", default=self.__content["species"])
        if not isinstance(species, str):
            species = str(species)
        if not (species in constants.SPECIES_LIST.__args__):
            raise Exception("Invalid species: %s" % species)
        
        n_cell = content.get("n_samples", "n_cell", default=self.__content["n_cell"])
        if not isinstance(n_cell, int):
            try:
                n_cell = int(n_cell)
            except:
                raise Exception("Invalid n_cell")
        
        n_batch = self.__get_value_optional(["n_batch"], content, int)
        if n_batch == 0:
            raise Exception("Invalid n_batch")

        omics = content.get("dataType", "omics", default=self.__content["omics"])
        if not isinstance(omics, list):
            omics = list(omics)
        for key in omics:
            if not key in constants.OMICS_LIST.__args__:
                raise Exception("Invalid omic type: %s" % key)
        
        unit_settings = content.get("unit_settings", default=self.__content["unit_settings"])
        for key in self.__content["unit_settings"]:
            val = unit_settings.get(key)
            try:
                val = UnitSettings(val)
            except:
                print("WARN: Invalid `unit_settings` for `%s`" % key)
                val = self.__content["unit_settings"][key]

        modified_date = content.get("modified_date", default=self.__content["modified_date"])
        if not (common.is_number(modified_date)):
            try:
                modified_date = float(modified_date)
            except:
                print("WARN: invalid `modified_date`")
                modified_date = self.__content["modified_date"]

        # ana_setting
        ana_setting = common.FuzzyDict(self.__get_value_optional(["ana_setting"], content, dict))
        input_type = ana_setting.get("inputType", default=self.__content["ana_setting"]["inputType"])
        if not input_type in constants.INPUT_FORMAT_LIST.__args__:
            input_type = self.__content["ana_setting"]["inputType"] * n_batch
        filter_setting = self.__get_value_optional(["filter"], ana_setting, dict, self.__content["ana_setting"]["filter"])
        try:
            filter_setting = FilterSetting(filter_setting)
        except:
            print("WARN: invalid `filter` in `ana_setting`")
            filter_setting = self.__content["ana_setting"]["filter"]
        norm_method = ana_setting.get("normMethod", default=self.__content["ana_setting"]["normMethod"])
        if not norm_method in constants.NORMALIZATION_LIST.__args__:
            norm_method = self.__content["ana_setting"]["normMethod"]
        try:
            ana_setting = AnaSetting(ana_setting)
        except:
            print("WARN: invalid `ana_setting`")
            ana_setting = self.__content["ana_setting"]

        unit = content.get("unit", default=self.__content["unit"])
        if not unit in constants.UNIT_LIST.__args__:
            print("WARN: Invalid `unit`")
            unit = self.__content["unit"]

        history = self.__get_value_optional(["history"], content, list)
        if len(history) == 0:
            history = self.__content["history"]
        try:
            for commit in history:
                commit = common.Commit(commit)
        except:
            history = self.__content["history"]

        misc = self.__get_value_optional(["misc"], content, dict)
        title = self.__get_value_optional(["title", "name"], content, str)
        papers = self.__get_value_optional(["papers"], content, list)
        abstract = self.__get_value_optional(["abstract"], content, str)
        author = self.__get_value_optional(["author"], content, list)
        tag = self.__get_value_optional(["tag"], content, list)
        shareTag = self.__get_value_optional(["shareTag"], content, list)
        is_public = history[0]["created_by"].endswith("@bioturing.com")
        version = self.__content["version"]

        self.__content = RunInfoStruc(hash_id=hash_id, species=species, n_cell=n_cell, n_batch=n_batch, omics=omics,
                                    unit_settings=unit_settings, modified_date=modified_date, ana_setting=ana_setting,
                                    unit=unit, misc=misc, title=title, papers=papers, abstract=abstract, author=author,
                                    tag=tag, shareTag=shareTag, is_public=is_public, history=history, version=version)
        self.__content = common.FuzzyDict(self.__content)
    
    def get(self, *args, **kwargs):
        return self.__content.get(*args, **kwargs)
    
    def write(self):
        self.__file.write(self.__content)