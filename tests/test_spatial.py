import unittest
import tempfile

from pydantic import ValidationError

class TestSpatial(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        unittest.TestCase.__init__(self, methodName=methodName)
        from walnut.spatial import LensInfo, Spatial

        self.__spatial_folder = tempfile.mkdtemp()
        self.spatial_info = Spatial(self.__spatial_folder)
        self.lens_info = LensInfo(self.__spatial_folder)

        assert self.lens_info.add(
            id = 1,
            name= "lens_1",
            width= 600,
            height= 600,
            raster_ids= [1, 2, 3],
            raster_names= ["channel1", "channel2", "channel3"],
            raster_types= ["multiplex", "multiplex", "multiplex"],
            lensMode= "PRIVATE",
        ) == True

    def test_update_spatial(self):
        assert self.spatial_info.update(width=1000, height=1000, diameter=[10, 10, 10], diameter_micron=[1, 1, 1])
        assert not self.spatial_info.update(width="abc", height=1000, diameter=[10, 10, 10], diameter_micron=[1, 1, 1])
        info = self.spatial_info.get()

        assert info.width == 1000
        assert info.height == 1000
        assert info.diameter == [10, 10, 10]
        assert info.diameter_micron == [1, 1, 1]

    def test_update_width(self):
        assert self.spatial_info.update_width(2000)
        assert not self.spatial_info.update_width("abc")
        info = self.spatial_info.get()
        assert info.width == 2000

    def test_update_height(self):
        assert self.spatial_info.update_height(3000)
        assert not self.spatial_info.update_height("abc")
        info = self.spatial_info.get()
        assert info.height == 3000

    def test_update_diameter(self):
        assert self.spatial_info.update_diameter([20, 20, 20, 20])
        assert not self.spatial_info.update_diameter([20, 20, 20, 20, "abc"])
        info = self.spatial_info.get()
        assert info.diameter == [20, 20, 20, 20]

    def test_update_diameter_micron(self):
        assert self.spatial_info.update_diameter_micron([2, 2, 2, 2])
        assert not self.spatial_info.update_diameter_micron([2, 2, "abc", 2, 2])
        
        info = self.spatial_info.get()
        assert info.diameter_micron == [2, 2, 2, 2]
        assert self.spatial_info.update_diameter_micron([1, 1, 1, 1])
        assert info.diameter_micron == [1, 1, 1, 1]
    
    def test_write_spatial(self):
        assert self.spatial_info.write() == True

    def test_add_lens(self):
        assert self.lens_info.add(
            id= 2,
            name= "lens_2",
            width= 1000,
            height= 1000,
            raster_ids= [4, 5, 6],
            raster_names= ["channel4", "channel5", "channel6"],
            raster_types= ["truecolor"],
            lensMode= "PUBLIC") == True

        image_info = self.lens_info.get(2)

        if image_info == False:
            return print("Image does not exist")

        assert str(image_info.id) == "2"
        assert image_info.name == "lens_2"
        assert image_info.width == 1000
        assert image_info.height == 1000
        assert image_info.raster_ids == [4, 5, 6]
        assert image_info.raster_names == ["channel4", "channel5", "channel6"]
        assert image_info.raster_types == ["truecolor"] and len(image_info.raster_types) == 1
        assert image_info.lensMode == "PUBLIC"

    def test_add_existing_lens(self):
        assert self.lens_info.add(id= 1,
            name= "lens_1",
            width= 1000,
            height= 1000,
            raster_ids= [7, 8, 9],
            raster_names= ["channel7", "channel8", "channel9"],
            raster_types= ["truecolor"],
            lensMode= "PUBLIC") == False

    def test_add_index_lens(self):
        assert self.lens_info.get_index(1) == 0

    def test_delete_lens(self):
        current_length = len(self.lens_info.getAll())

        assert self.lens_info.delete(1) == True
        assert len(self.lens_info.getAll()) == current_length - 1

    def test_write_lens(self):
        assert self.lens_info.write() == True

    def test_validation_error(self):
        assert self.lens_info.add(id= 3,
            name= "lens_3",
            width= 1000,
            height= 1000,
            raster_ids= [7, 8, 9],
            raster_names= ["channel7", "channel8", "channel9"],
            raster_types= ["multiplex", "truecolor"],
            lensMode= "PUBLIC") == False

        assert self.lens_info.add(id= 3,
            name= "lens_3",
            width= 1000,
            height= 1000,
            raster_ids= [7, 8, 9],
            raster_names= ["channel7", "channel8", "channel9"],
            raster_types= ["truecolor", "truecolor"],
            lensMode= "PUBLIC") == False

        assert self.lens_info.add(id= 3,
            name= "lens_3",
            width= 1000,
            height= 1000,
            raster_ids= [7, 8, 9],
            raster_names= ["channel7", "channel8", "channel9"],
            raster_types= ["aaaa", "aaaa"],
            lensMode= "PUBLIC") == False