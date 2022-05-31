from typing import TypeVar, Generic, Any
from abc import ABC, abstractmethod
import json

from walnut.models import Category, Metalist, GeneCollections, RunInfo, CategoryMeta, MetaDimred, SingleDimred, SpatialInfo, LensImageInfo
from walnut import common

OUT_TYPE = TypeVar("OUT_TYPE")

class IOConverter(ABC, Generic[OUT_TYPE]):
    @staticmethod
    @abstractmethod
    def from_str(s: Any) -> OUT_TYPE:
        pass

    @staticmethod
    @abstractmethod
    def to_str(content: OUT_TYPE) -> Any:
        pass

class IOAsIs(IOConverter[OUT_TYPE]):
    @staticmethod
    def from_str(s: OUT_TYPE) -> OUT_TYPE:
        return s

    @staticmethod
    def to_str(content: OUT_TYPE) -> OUT_TYPE:
        return content

class IOJSON(IOConverter[dict]):
    @staticmethod
    def from_str(s: str) -> dict:
        return json.loads(s)

    @staticmethod
    def to_str(content: dict) -> str:
        return json.dumps(content)

class IOCategory(IOConverter[Category]):
    @staticmethod
    def from_str(s: str) -> Category:
        content = json.loads(s)
        if isinstance(content, dict):
            return Category.parse_obj(content)
        else:
            return Category(clusters=content)

    @staticmethod
    def to_str(content: Category) -> str:
        return content.json()

class IOMetalist(IOConverter[Metalist]):
    @staticmethod
    def from_str(s: str) -> Metalist:
        obj = json.loads(s)
        if "content" not in obj:
            obj = {"content": obj}

        invalid_categories = []
        for category_name, category in obj["content"].items():
            try:
                if not "id" in category:
                    category["id"] = category_name
                CategoryMeta.parse_obj(category)
            except Exception as e:
                print("WARNING: Unable to parse category %s due to error: %s"
                        % (category_name, str(e)))
                invalid_categories.append(category_name)

        for invalid_cate in invalid_categories:
            del obj["content"][invalid_cate]

        return Metalist.parse_obj(obj)

    @staticmethod
    def to_str(content: Metalist) -> str:
        return content.json()

class IOGallery(IOConverter[GeneCollections]):
    @staticmethod
    def from_str(s: str) -> GeneCollections:
        return GeneCollections(__root__=json.loads(s))

    @staticmethod
    def to_str(content: GeneCollections) -> str:
        return content.json()

class IORunInfo(IOConverter[RunInfo]):
    @staticmethod
    def from_str(s: str) -> RunInfo:
        content = common.FuzzyDict(json.loads(s))
        content["hash_id"] = content.get("hash_id", "study_id")
        content["species"] = content.get("index_type", "species")
        content["n_cell"] = content.get("n_cell", "n_samples")
        content["omics"] = content.get("dataType", "omics", default=["RNA"])
        content["title"] = content.get("title", "name", default="Untitled study")
        return RunInfo.parse_obj(content)

    @staticmethod
    def to_str(content: RunInfo) -> str:
        return content.json()

class IOMetaDimred(IOConverter[MetaDimred]):
    @staticmethod
    def from_str(s: str) -> MetaDimred:
        return MetaDimred.parse_obj(json.loads(s))

    @staticmethod
    def to_str(content: MetaDimred) -> str:
        return content.json()

class IOSingleDimred(IOConverter[SingleDimred]):
    @staticmethod
    def from_str(s: str) -> SingleDimred:
        return SingleDimred.parse_obj(json.loads(s))

    @staticmethod
    def to_str(content: SingleDimred) -> str:
        return content.json()

class IOSpatial(IOConverter[SpatialInfo]):
    @staticmethod
    def from_str(s: str) -> SpatialInfo:
        return SpatialInfo.parse_raw(s)

    @staticmethod
    def to_str(content: SpatialInfo) -> str:
        return content.json()

class IOLens(IOConverter[LensImageInfo]):
    @staticmethod
    def from_str(s: str) -> LensImageInfo:
        return LensImageInfo(__root__=json.loads(s))

    @staticmethod
    def to_str(content: LensImageInfo) -> str:
        return content.json()