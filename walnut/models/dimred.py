from pydantic import BaseModel, root_validator
from typing import List, Optional, Dict
from walnut.models import History
from walnut import common, constants

class Param(BaseModel):
    omics: Optional[constants.OMICS_LIST] = "RNA"
    correction: Optional[str] = "none"

class SingleDimredBase(BaseModel):
    id: Optional[str] = None
    name: str
    size: List[int]
    history: List[History] = [common.create_history()]
    param: Optional[Param] = Param()

class SingleDimred(SingleDimredBase):
    coords: Optional[List[List[float]]] = None
    slide: Optional[List[str]] = None

    @root_validator(pre=True)
    def either_coords_or_slide_must_exist(cls, values):
        coords, slide = values.get("coords"), values.get("slide")
        if coords is None and slide is None:
            raise ValueError("Either coords or slide must be present in Dimred content")
        return values

    @root_validator(pre=False)
    def delete_extraneous_values(cls, values):
        coords, slide = values.get("coords"), values.get("slide")
        if coords is None:
            del values["coords"]
        if slide is None:
            del values["slide"]
        return values

    @property
    def is_multislide(self):
        return getattr(self, "slide", False)

class MetaDimred(BaseModel):
    data: Dict[str, SingleDimredBase] = {}
    default: Optional[str] = ""
    version: Optional[int] = 1
    bbrowser_version: Optional[str] = ""

    def get_dimred_ids(self) -> List[str]:
        return [x for x in self.data.keys()]

    def add_dimred(self, dimred_meta: SingleDimredBase):
        if dimred_meta.id in self.data:
            raise ValueError("Dimred id %s already exists" % dimred_meta.id)

        self.data[dimred_meta.id] = dimred_meta

    def remove_dimred(self, dimred_id: str):
        if not dimred_id in self.data:
            raise ValueError("Id %s not present" % dimred_id)
        del self.data[dimred_id]