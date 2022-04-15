from walnut import constants
from typing import List
from pydantic import BaseModel

class GeneCollectionItem(BaseModel):
    name: str
    id: str
    created_at: constants.NUM
    last_modified: constants.NUM
    features: List[str]

class GeneCollection(BaseModel):
    name: str
    type: constants.OMICS_LIST
    items: List[GeneCollectionItem]
    id: str
    created_at: constants.NUM
    last_modified: constants.NUM
    created_by: str

class GeneCollections(BaseModel):
    __root__: List[GeneCollection]
