import os
from walnut import constants, common
from typing import TypedDict, Union
import json

class Item(TypedDict):
    name: str
    id: str
    created_at: constants.NUM
    features: list[str]

class Collection(TypedDict):
    name: str
    type: constants.OMICS_LIST
    items: list[Item]
    id: str
    created_at: constants.NUM
    last_modified: constants.NUM
    created_by: str

class Gallery:
    def __init__(self, gallery_folder, TextFile: common.FileIO):
        self.__dir = gallery_folder
        self.__TextFile = TextFile
        self.__old_gallery = common.JSONFile(os.path.join(self.__dir, "gene_gallery.json"), self.__TextFile)
        self.__gallery = common.JSONFile(os.path.join(self.__dir, "gene_gallery_2.json"), self.__TextFile)
        self.collections: list[Collection] = []
    
    def from_json(self, json_str: str):
        self.collections = json.loads(json_str)
    
    def to_json(self) -> str:
        return json.dumps(self.collections)

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
        if len(self.collections) == 0:
            raise Exception("Cannot write an empty gallery")
        self.__gallery.write(self.collections)
    
    def get(self, col_id: str, straighten: bool=True, unique: bool=True) -> Union[list[list], list[str]]:
        """Get a list of item IDs given a collection ID"""
        col = self.collections[self.__get_collection_index(col_id)]
        result = []
        for item in col["items"]:
            if straighten:
                for ft in item["features"]:
                    if (not unique) or (ft not in result):
                        result.append(ft)
            else:
                result.append(item["features"])
        return result
    
    def __get_collection_index(self, col_id):
        for i, col in enumerate(self.collections):
            if col["id"] == col_id:
                return i
        raise Exception("%s does not exist" % col_id)

    def add_item(self, col_id: str, name: str, gene_id: list[str]):
        now = common.get_timestamp()
        item = Item(name=name, id=common.create_uuid(), features=gene_id,
                           created_at=now, last_modified=now)
        i = self.__get_collection_index(col_id)
        self.collections[i]["items"].append(item)
        return item["id"]
    
    def create_empty_collection(self, name: str, ft_type: constants.OMICS_LIST="RNA") -> str:
        now = common.get_timestamp()
        col = Collection(name=name, type=ft_type, id=common.create_uuid(), items=[],
                                created_at=now, last_modified=now)
        self.collections.append(col)
        return col["id"]

    def create_gene_collection(self, name: str, gene_id: list[str]) -> str:
        """Create a gene collection given a list of genes"""
        col_id = self.create_empty_collection(name)
        for gene in gene_id:
            self.add_item(col_id, gene, [gene]) # FIXME: Handle gene name and ID
        return col_id
