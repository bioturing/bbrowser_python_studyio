from pydantic import BaseModel
from typing import Dict, List

class SpotCellTypes(BaseModel):
    __root__: Dict[str, List[float]]

class GeneWeight(BaseModel):
    __root__:  List[float]

class TopicCoordinates(BaseModel):
    x: List[float]
    y: List[float]
    topic: List[int]
    frequency: List[float] 

class DeconvolutionInfo(BaseModel):
    spot_celltypes: SpotCellTypes
    cell_types: Dict[str, List[float]]
    genes: List[str]
    topic_coordinates: TopicCoordinates


