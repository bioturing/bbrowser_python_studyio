import os
from walnut import constants, common
from walnut.converters import IOGallery, IOJSON
from walnut.FileIO import FileIO
from walnut.readers import Reader
from walnut.models import GeneCollections, GeneCollectionItem, GeneCollection
from typing import Union, List
import json

class Gallery:
    def __init__(self, gallery_folder: str, reader: Reader):
        self.__dir = gallery_folder
        self.__old_gallery = FileIO(os.path.join(self.__dir, "gene_gallery.json"), reader, IOJSON)
        self.__gallery = FileIO(os.path.join(self.__dir, "gene_gallery_2.json"), reader, IOGallery)
        self.collections = GeneCollections(__root__=[])
    
    def from_json(self, json_str: str):
        self.collections = GeneCollections(__root__=json.loads(json_str))

    def to_json(self) -> str:
        return self.collections.json()

    def exists(self) -> bool:
        return self.__old_gallery.exists() or self.__gallery.exists()

    def read(self):
        if not self.exists():
            raise Exception("No gallery data to read")
        
        if self.__gallery.exists():
            self.collections = self.__gallery.read()
            return
        
        if self.__old_gallery.exists():
            raise Exception("Cannot read old gallery data yet") # FIXME
    
    def write(self):
        if len(self.collections.__root__) == 0:
            raise Exception("Cannot write an empty gallery")
        self.__gallery.write(self.collections)
    
    def get(self, col_id: str, straighten: bool=True, unique: bool=True) -> Union[List[list], List[str]]:
        """Get a list of item IDs given a collection ID"""
        col = self.collections.__root__[self.__get_collection_index(col_id)]
        result = []
        for item in col.items:
            if straighten:
                for ft in item.features:
                    if (not unique) or (ft not in result):
                        result.append(ft)
            else:
                result.append(item["features"])
        return result
    
    def __get_collection_index(self, col_id) -> int:
        for i, col in enumerate(self.collections.__root__):
            if col.id == col_id:
                return i
        raise Exception("%s does not exist" % col_id)

    def add_item(self, col_id: str, name: str, gene_id: List[str]) -> str:
        now = common.get_timestamp()
        item = GeneCollectionItem(name=name, id=common.create_uuid(), features=gene_id,
                           created_at=now, last_modified=now)
        i = self.__get_collection_index(col_id)
        self.collections.__root__[i].items.append(item)
        return item.id
    
    def create_empty_collection(self, name: str, ft_type: constants.OMICS_LIST="RNA") -> str:
        now = common.get_timestamp()
        col = GeneCollection(name=name, type=ft_type, id=common.create_uuid(), items=[],
                                created_at=now, last_modified=now, created_by="walnut")
        self.collections.__root__.append(col)
        return col.id
