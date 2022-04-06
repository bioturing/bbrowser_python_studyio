from typing import Optional
from pydantic import BaseModel

class History(BaseModel):
    created_by: Optional[str]
    created_at: Optional[float]
    hash_id: Optional[str]
    description: Optional[str]
    message: Optional[str]