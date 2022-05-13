from pydantic import BaseModel, validator
from typing import List

from walnut import constants

class SpatialInfo(BaseModel):

    class Config:
        validate_assignment = True

    width: float = 0
    height: float = 0
    diameter: List[float] = []
    diameter_micron: List[float] = []
    version: int = 1
    
class ImageInfo(BaseModel):

    class Config:
        validate_assignment = True

    id: constants.LENSID
    name: str
    width: float
    height: float
    raster_ids: List[constants.LENSID]
    raster_names: List[str]
    raster_types: List[constants.LENS_IMAGE_TYPE]
    lensMode: constants.LENS_MODE

    @validator("raster_types", pre=True)
    def validate_raster_types(cls, v):
        raster_length = len(v)
        # if multiplex, length of raster_types is equal to length of multiplex
        if 'multiplex' in v and v.count('multiplex') != raster_length:
            raise ValueError("WARNING: raster_types of multiplex requires 3 in length")

        # if truecolor, length of raster_types is 1
        if 'truecolor' in v and not (v.count('truecolor') == raster_length and raster_length == 1):
            raise ValueError("WARNING: raster_types of truecolor requires 1 in length")

        return v

class LensImageInfo(BaseModel):
    __root__: List[ImageInfo]