from pydantic import BaseModel
from typing import List, Optional

class DimredData(BaseModel):
	id: Optional[str]=None
	name: str
	size: List[int]
	history: List[dict]=None
	param: dict

class DimredDataBasic(DimredData):
	coords: List[List[int]]

class DimredDataMultislide(DimredData):
	slide: List[str]
