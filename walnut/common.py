import time
from uuid import uuid4
from typing import Collection, List, Dict, Any, TypeVar, Generic, Type, Union
from scipy import sparse
import numpy
from abc import ABC, abstractmethod
import os
import json
from walnut.models import History
from typing import Type, TypeVar, Generic
from walnut import constants
import shutil

FileContent = TypeVar("FileContent")

class FileIO(ABC, Generic[FileContent]):
    """(deprecated)"""
    def __init__(self, filepath: str):
        self.path = filepath

    def exists(self) -> bool:
        return os.path.isfile(self.path)

    @abstractmethod
    def read(self) -> FileContent:
        pass

    @abstractmethod
    def write(self, content: FileContent) -> None:
        pass

class TextFile(FileIO[str]):
    def read(self) -> str:
        with open(self.path) as fopen:
            return fopen.read()

    def write(self, text: str):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as fopen:
            fopen.write(text)

class JSONFile(FileIO[dict]):
    def __init__(self, filepath: str, CustomTextFile: Type[TextFile]):
        super().__init__(filepath)
        self.__file = CustomTextFile(filepath)

    def read(self) -> dict:
        json_str = self.__file.read()
        return json.loads(json_str)

    def write(self, obj: dict):
        json_str = json.dumps(obj)
        self.__file.write(json_str)

class FuzzyDict(dict):
    """A dictionary where value can be obtained with multiple keys"""
    def get(self, *keys, default=None):
        for key in keys:
            val = super().get(key)
            if not val is None:
                return val
        return default

    def __len__(self):
        return len(self.keys())

def get_timestamp():
    return time.time() * 1000

def create_uuid():
    return str(uuid4()).replace("-", "")

def create_history(creator="walnut", description="Created automatically") -> History:
    return History(created_by=creator, created_at=time.time(),
                    hash_id=create_uuid(),
                    description=description)

def find_indices_in_list(needles: Collection, haystack: Collection) -> List[int]:
    if len(numpy.unique(list(haystack))) != len(haystack):
        raise ValueError("haystack must not contain any duplicate items")

    index: Dict[Any, int] = {}
    for i, item in enumerate(haystack):
        index[item] = i

    return [index.get(item, -1) for item in needles]

def is_number(x) -> bool:
    return isinstance(x, int) or isinstance(x, float)

def get_pkg_data():
    return os.path.join(os.path.dirname(constants.__file__), "data")

def exc_to_str(e):
    return "%s: %s" % (e.__class__.__name__, str(e))

def make_unique(x: List[str]) -> List[str]:
    """ Create a unique list of strings """
    memo: Dict[str, int] = {}
    for i, val in enumerate(x):
        count = memo.get(val, 0)
        if count > 0:
            count += 1
            memo[val] = count
            x[i] = '%s_%s' % (val, count)
        else:
            memo[val] = 1
    return x

def get_density(mtx: Union[sparse.csc_matrix, sparse.csr_matrix]) -> float:
    return mtx.nnz / mtx.shape[0] / mtx.shape[1]

def is_dense(mtx: Union[sparse.csc_matrix, sparse.csr_matrix], threshold: float=2/3) -> bool:
    """
    Determine if a matrix is dense or sparse based on `threshold`
    2/3 is ad-hoc value
    """
    return get_density(mtx) > threshold

def clear_folder(x: str):
    """Ensures a folder exists and empty"""
    if os.path.isdir(x):
        shutil.rmtree(x)
    os.makedirs(x)