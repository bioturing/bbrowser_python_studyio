from pydantic import BaseModel, validator, root_validator
from walnut import constants
from typing import Optional, Union, List

class History(BaseModel):
    created_by: str
    created_at: constants.NUM = 2409 # Some history does not have this!
    hash_id: str
    message: Optional[str]
    description: Optional[str]

    @validator("description", pre=True, always=True)
    def set_description(cls, desc, values: dict):
        # Handle description = None or = {}
        if not isinstance(desc, str):
            desc = values.get("message")
            if not isinstance(desc, str):
                desc = "None"
        return desc

    @validator("created_by", "hash_id", pre=True, always=True)
    def handle_weird_string(cls, v):
        if isinstance(v, list):
            v = v[0]
        if isinstance(v, dict):
            v = "Invalid value found by walnut while parsing"
        return v

    @validator("created_at", pre=True, always=True)
    def handle_weird_number(cls, v):
        if isinstance(v, list):
            v = v[0]
        if isinstance(v, dict):
            v = 2409
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