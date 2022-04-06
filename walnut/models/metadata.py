from typing import Optional, List, Union, Dict
from pydantic import BaseModel, validator
import numpy

from walnut.models import History
from walnut import constants

class CategoryBase(BaseModel):
    id: Optional[str]
    name: Optional[str]
    type: Optional[str]
    clusterName: Optional[List[str]]
    clusterLength: Optional[List[int]]
    history: Optional[List[History]]

    @validator("type")
    def type_must_in_list(cls, v):
        if v not in [constants.METADATA_TYPE_CATEGORICAL, constants.METADATA_TYPE_NUMERIC]:
            raise ValueError("\"type\" must be either \"%s\" or \"%s\""
                                % (constants.METADATA_TYPE_CATEGORICAL, constants.METADATA_TYPE_NUMERIC))
        return v

    @validator("clusterName", "clusterLength", pre=True)
    def ignore_if_numerical_type(cls, v, values: dict):
        if values.get("type") == constants.METADATA_TYPE_NUMERIC:
            return []
        else:
            return v

class CategoryMeta(CategoryBase):
    id: str
    name: str
    history: List[History]
    type: str = constants.METADATA_TYPE_CATEGORICAL
    clusterName: List[str]
    clusterLength: List[int]

class Category(CategoryBase):
    clusters: List[Union[int, float]]

class Metalist(BaseModel):
    version: Optional[int]
    default: Optional[str]
    content: Dict[str, CategoryMeta]

    def get_category_ids(self) -> List[str]:
        return [x for x in self.content.keys()]

    def remove_category(self, category_id: str) -> None:
        del self.content[category_id]

    def get_category_meta(self, category_id: str) -> CategoryMeta:
        return self.content[category_id]

    def get_category_data(self, category_id: str, category: Category) -> numpy.ndarray:
        meta = self.get_category_meta(category_id)
        if meta.type == "numeric":
            res = numpy.array(category.clusters)
        else:
            cluster_names = meta.clusterName
            indices = [int(x) for x in category.clusters]
            res = numpy.array(cluster_names)[indices]
        return res

    def add_category(self, category: CategoryMeta):
        if category.id in self.content:
            raise ValueError("Duplicate category id")

        self.content[category.id] = category

