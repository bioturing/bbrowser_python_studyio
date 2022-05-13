from pydantic import BaseModel
from typing import List

from walnut import constants

class SpatialInfo(BaseModel):
    width: float = 0
    height: float = 0
    diameter: List[float] = []
    diameter_micron: List[float] = []
    version: int = 1
    
class ImageInfo(BaseModel):
    id: constants.LENSID
    name: str
    width: float
    height: float
    raster_id: List[constants.LENSID]
    raster_names: List[str]
    raster_types: List[constants.LENS_IMAGE_TYPE]
    lensMode: constants.LENS_MODE

class LensImageInfo(BaseModel):
    __root__: List[ImageInfo]