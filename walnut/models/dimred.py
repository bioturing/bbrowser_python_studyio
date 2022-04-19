from pydantic import BaseModel
from typing import List, Optional
from walnut.models import History
from walnut import common

class DimredData(BaseModel):
	id: Optional[str]=None
	name: str
	size: List[int]
	history: Optional[List[History]] = [common.create_history()]
	param: dict

class DimredDataBasic(DimredData):
	coords: List[List[int]]

class DimredDataMultislide(DimredData):
	slide: List[str]
