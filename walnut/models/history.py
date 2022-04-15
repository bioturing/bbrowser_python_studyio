from pydantic import BaseModel, validator
from walnut import constants
from typing import Optional

class History(BaseModel):
    created_by: str
    created_at: constants.NUM
    hash_id: str
    message: Optional[str]
    description: Optional[str]
    
    @validator("description", always=True)
    def set_description(cls, desc, values: dict) -> None:
        if not desc:
            desc = values.get("message")
            assert isinstance(desc, str)
        return desc