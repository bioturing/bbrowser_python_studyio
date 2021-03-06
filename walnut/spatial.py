import os
from walnut import constants
from walnut.converters import IOSpatial, IOLens
from walnut.FileIO import FileIO
from walnut.readers import Reader, TextReader
from walnut.models import SpatialInfo, ImageInfo, LensImageInfo
from typing import List, Union, Optional
from walnut.constants import LENSID
from walnut import common
from pydantic import ValidationError

class LensInfo:
    def __init__(self, spatial_folder: str, reader: Reader = TextReader()):
        self.__dir = spatial_folder
        self.__lens_image_info = FileIO(os.path.join(self.__dir, "lens_image_info.json"), reader, IOLens)

        self.lens_image_info = LensImageInfo(__root__=[])

    def exists(self) -> bool:
        return self.__lens_image_info.exists()

    def read(self) -> bool:
        if not self.exists():
            print("WARNING: No Lens info to read")
            return False

        self.lens_image_info = self.__lens_image_info.read()
        return True

    def write(self):
        self.__lens_image_info.write(self.lens_image_info)

        return True

    def get(self, id: LENSID) -> Union[ImageInfo, bool]:
        for image_info in self.lens_image_info.__root__:
            if str(image_info.id) == str(id):
                return image_info

        return False

    def add(self,
        id: constants.LENSID,
        name: str,
        width: float,
        height: float,
        raster_ids: List[constants.LENSID],
        raster_names: List[str],
        raster_types: List[constants.LENS_IMAGE_TYPE],
        lensMode: constants.LENS_MODE
    ):
        # check if id alread exists
        if self.get(id):
            print("WARNING: %s already exists" % id)
            return False
        # try to init ImageInfo
        try:
            image_info = ImageInfo(id = id,
                                name = name,
                                width = width,
                                height = height,
                                raster_ids = raster_ids,
                                raster_names = raster_names,
                                raster_types = raster_types,
                                lensMode = lensMode)

            self.lens_image_info.__root__.append(image_info)

            return True
        except Exception as e:
            print("WARNING: %s" % e)
            return False

    def getAll(self) -> List[ImageInfo]:
        return self.lens_image_info.__root__

    def get_index(self, id: LENSID) -> int:
        for i, image_info in enumerate(self.lens_image_info.__root__):
            if str(image_info.id) == str(id):
                return i

        print("WARNING: %s does not exist" % id)
        return False

    def delete(self, id: LENSID):
        index = self.get_index(id)
        del self.lens_image_info.__root__[index]

        return True


class Spatial:
    def __init__(self,
        spatial_folder: str,
        spatial_info: Optional[SpatialInfo] = None,
        reader: Reader = TextReader()
    ):
        self.__dir = spatial_folder
        self.__spatial_info = FileIO(os.path.join(self.__dir, "info.json"), reader, IOSpatial)

        self.spatial_info = spatial_info if spatial_info else self.read()

    def exists(self):
        return self.__spatial_info.exists()

    def get(self) -> SpatialInfo:
        return self.spatial_info

    def read(self):
        if not self.exists():
            print("WARNING: No spatial info to read")
            return SpatialInfo()

        return self.__spatial_info.read()

    def write(self):
        self.__spatial_info.write(self.spatial_info)

        return True

    def update(self,
        width: float,
        height: float,
        diameter: Union[List[float], float],
        diameter_micron: Union[List[float], float],
        version: int = 1
    ):
        try:
            self.spatial_info = SpatialInfo(
                width=width,
                height=height,
                diameter=diameter,
                diameter_micron=diameter_micron,
                version=version
            )
            return True
        except ValidationError as e:
            print(common.exc_to_str(e))
            return False

    def update_width(self, width: float):
        try:
            self.spatial_info.width = width
            return True
        except ValidationError as e:
            print(common.exc_to_str(e))
            return False

    def update_height(self, height: float):
        try:
            self.spatial_info.height = height
            return True
        except ValidationError as e:
            print(common.exc_to_str(e))
            return False

    def update_diameter(self, diameter: List[float]):
        try:
            self.spatial_info.diameter = diameter
            return True
        except ValidationError as e:
            print(common.exc_to_str(e))
            return False


    def update_diameter_micron(self, diameter_micron: List[float]):
        try:
            self.spatial_info.diameter_micron = diameter_micron
            return True
        except ValidationError as e:
            print(common.exc_to_str(e))
            return False


