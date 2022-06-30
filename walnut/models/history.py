from pydantic import BaseModel, validator, root_validator
from walnut import constants
from typing import Optional, Union, List

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

    @validator("created_by", "created_at", "hash_id", "description", pre=True, always=True)
    def unlist(cls, v):
        if isinstance(v, list):
            v = v[0]
        return v

    @root_validator(pre=True)
    def check_values(cls, values):
        # Backward compat
        if 'createdBy' in values:
            values['created_by'] = values.get('createdBy')
        if 'createdAt' in values:
            values['created_at'] = values.get('createdAt')
        if 'hashId' in values:
            values['hash_id'] = values.get('hashId')
        return values