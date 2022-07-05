from typing import Optional, List, Union, Dict
from pydantic import BaseModel, validator, root_validator
import numpy
from walnut.models import History
from walnut import constants, common

class CategoryBase(BaseModel):
    id: Optional[str]=None
    name: Optional[str]=None
    type: Optional[constants.METADATA_TYPE_LIST]=None
    clusterName: List[str] = []
    clusterLength: List[int] = []
    history: List[History]=[]

    @validator("clusterName", "clusterLength", pre=True, always=True)
    def ignore_if_numerical_type(cls, v, values: dict):
        if values.get("type") == constants.METADATA_TYPE_NUMERIC:
            return []
        else:
            return v

    @validator("clusterName")
    def first_name_unassigned(cls, v, values: dict):
        if values.get("type") == constants.METADATA_TYPE_CATEGORICAL:
            if len(v) == 0:
                raise ValueError("\"clusterName\" must not be empty")
            if v[0] != constants.BIOTURING_UNASSIGNED:
                raise ValueError("First value in \"clusterName\" must be \"%s\", not \"%s\""
                                    % (constants.BIOTURING_UNASSIGNED, v[0]))
        return v

    @validator("clusterLength", pre=True, always=True)
    def ignore_weird_value(cls, v):
        if not isinstance(v, list):
            print("WARNING: clusterLength is not a valid list", v)
            v = []
        return v

    @validator("id", "name", "type", pre=True, always=True)
    def unlist(cls, v):
        if isinstance(v, list):
            v = v[0]
        return v

    @validator("history", pre=True)
    def check_history(cls, history_list):
        try:
            for v in history_list:
                History(**v)
        except Exception as e:
            # Return dummy history when all else fail
            history_list = [History(created_by = "walnut", created_at=2409, hash_id = common.create_uuid(), description="Dummy history")]
        return history_list


class CategoryMeta(CategoryBase):
    id: str
    name: str
    history: List[History] = [common.create_history()]
    type: constants.METADATA_TYPE_LIST = constants.METADATA_TYPE_CATEGORICAL
    clusterName: List[str] = []
    clusterLength: List[int] = []

    @root_validator(pre=True)
    def check_all(cls, values):
        v = values.get("history")
        if not isinstance(v, list): # history is not a list
            values['history'] = [v]
        return values

class Category(CategoryBase):
    clusters: Union[List[Union[int, None]], List[Union[float, None]]]

    @validator("clusters", each_item=True, pre=True)
    def check_number(cls, v):
        for i, value in enumerate(v):
            if not isinstance(value, (int, float)):
                v[i] = None
        return v

class Metalist(BaseModel):
    version: Optional[int] = None
    default: Optional[str] = None
    content: Dict[str, CategoryMeta]

    @validator("content", pre=True)
    def set_content_id(cls, content):
        for id in content:
            if not "id" in content[id]:
                content[id]["id"] = id
            content[id] = CategoryMeta.parse_obj(content[id])
        return content

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

# class MetadataType(BaseModel):
#     typeList: Dict[str, Dict[str, str]] = {
#         constants.METADATA_TYPE_CATEGORICAL: {"name": "Category", "desc": "Labels simply are strings"},
#         constants.METADATA_TYPE_NUMERIC: {"name": "Numeric", "desc": "Labels are numbers"}
#     }
#     cellTypes: Dict = {}
#     maxClusters: int

#     def get(self, type) -> Dict:
#         if type:
#             return self.typeList.get(type, {})
#         else:
#             return self.typeList

    # def is_category(self, metadata) -> boolean:
    #     return metadata and metadata.type == constants.METADATA_TYPE_CATEGORICAL

    # def is_numeric(self, metadata) -> boolean:
    #     return metadata and metadata.type == constants.METADATA_TYPE_NUMERIC

    # def convert_to_category(self, metadata):
    #     if self.is_cell_type(metadata):
    #         metadata.clusterName = list(map(lambda x: self.cellTypes.get(x) or constants.UNASSIGNED))
    #     elif self.is_numeric(metadata):
    #         new_cluster_name = list(float(x) for x in set(filter(lambda x: x == x, metadata.clusters)))
    #         assert (new_cluster_name.length < self.maxClusters), f"Can not convert to category, this metadata have more than {max_clusters} labels."
    #         mapping = {}
    #         new_cluster_name = ['Unassigned'] + list(sorted(new_cluster_name))
    #         for idx, label in enumerate(new_cluster_name):
    #             mapping[label] = idx
    #         cluster_length = [0]*len(new_cluster_name)
    #         for idx, cluster in enumerate(metadata.clusters):
    #             cluster = float(cluster)
    #             metadata.clusters[idx] = mapping[cluster] if cluster and cluster == cluster else 0
    #             cluster_length[mapping[cluster]] += 1
    #         metadata.clusterName = new_cluster_name
    #         metadata.clusterLength = cluster_length
    #     return metadata

    # def convert_to_numeric(self, metadata):
    #     for idx in range(len(metadata.clusterName)):
    #         if idx == 0: continue
    #         assert ((float(metadata.clusterName[idx]) == float(metadata.clusterName[idx])) or (metadata.clusterName[idx] == metadata.clusterName[idx])), "Name of clusters must be numeric"
    #     for idx, cluster in enumerate(metadata.clusters):
    #         metadata.clusters[idx] = float('NaN') if cluster == 0 else float(metadata.clusterName[cluster])
    #     return metadata

    # def convert(self, metadata, type):
    #     if self.typeList.get(type):
    #         metadata.history.append(common.create_commit({"description": f"Change type from {self.typeList[metadata.type]['name']} to {self.typeList[type]['name']}"}))
    #         switcher = {
    #             constants.METADATA_TYPE_CATEGORICAL: self.convert_to_category(metadata),
    #             constants.METADATA_TYPE_NUMERIC: self.convert_to_numeric(metadata)
    #         }
    #         metadata = switcher.get(type)
    #         metadata.type = type
    #         return metadata
    #     return None

class GraphClusterInfo(BaseModel):
    id: str
    name: str
    history: List[History]
    length: int
    version: int
    parent_id: str

class GraphClusterDetail(GraphClusterInfo):
    img: str = "null"
    selectedArr: List[int]