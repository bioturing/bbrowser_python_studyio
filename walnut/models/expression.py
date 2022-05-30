from pydantic import BaseModel, root_validator, validator
from typing import List, Optional, Literal, Union
from walnut import constants
from scipy import sparse

class ExpressionData(BaseModel):
    raw_matrix: Union[sparse.csc_matrix, sparse.csr_matrix]
    norm_matrix: Union[sparse.csc_matrix, sparse.csr_matrix]
    barcodes: List[str]
    features: List[str]
    feature_type: List[Literal[constants.FEATURE_TYPES]]

    class Config:
        arbitrary_types_allowed=True


    @validator("raw_matrix", pre=False)
    def check_raw(cls, v):
        if v.min() < 0:
            raise ValueError("Raw count matrix with negative values are not supported")
        return v.tocsc()

    @validator("norm_matrix", pre=False)
    def check_norm(cls, v):
        return v.tocsc()


    @root_validator(pre=False, skip_on_failure=True)
    def check_barcode_feature(cls, values):
        barcodes, features = values.get("barcodes"), values.get("features")
        feature_type = values.get("feature_type")
        raw_matrix, norm_matrix = values.get("raw_matrix"), values.get("norm_matrix")

        if not raw_matrix.shape == norm_matrix.shape:
            raise ValueError("Shape of raw_matrix and norm_matrix must match")

        if not len(barcodes) == raw_matrix.shape[1]:
            raise ValueError("Number of cells must match number of col in raw_matrix")

        if not len(features) == raw_matrix.shape[0]:
            raise ValueError("Number of features must match number of row in raw_matrix")

        if not len(feature_type) == len(features):
            raise ValueError("Length of feature type and features must match")

        if not len(set(features)) == len(features):
            raise ValueError("`features` must be a list of unique values")

        if not len(set(barcodes)) == len(barcodes):
            raise ValueError("`barcodes` must be a list of unique values")

        return values
