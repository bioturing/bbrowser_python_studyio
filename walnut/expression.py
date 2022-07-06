from typing import Union, List, Literal, Tuple, get_args, Any
import os
import h5py
import pandas as pd
import numpy as np
from scipy import sparse
import scanpy as sc
import anndata
from walnut.models import ExpressionData
from walnut.common import read_sparse_mtx, get_1d_dataset
from walnut import constants
from anndata._core.sparse_dataset import SparseDataset

class SparseExpression(SparseDataset):
    """
    Interface for on-disk sparse matrix from AnnData
    Not used yet. Might be useful for big study.
    """

    @property
    def format_str(self) -> str:
        return "csc"

    @property
    def shape(self) -> Tuple[int, int]:
        shape = self.group["shape"]
        return tuple(shape)  # type: ignore

class Expression:
    def __init__(self, h5path):
        self.path = h5path
        self.__expression_data = None

    def read_expression_data(self) -> None:
        """
        Load all data from matrix.hdf5
        """
        if not self.exists:
            print("WARNING: No matrix.hdf5 found. This study has not been written yet")
            return

        if self.raw_matrix is None:
            return

        if self.norm_matrix is None:
            return

        if self.barcodes is None:
            return

        if self.features is None:
            return

        if self.feature_type is None:
            return

        self.__expression_data = ExpressionData(raw_matrix=self.raw_matrix,
                                                norm_matrix=self.norm_matrix,
                                                barcodes = self.barcodes,
                                                features = self.features,
                                                feature_type=self.feature_type)


    @property
    def exists(self) -> bool:
        if not os.path.exists(self.path):
            print("WARNING: No matrix.hdf5 is found at %s" % self.path)
        return os.path.exists(self.path)


    @property
    def features(self) -> Union[List[str], None]:
        if self.__expression_data:
            return self.__expression_data.features

        if not self.exists:
            print("WARNING: No matrix.hdf5 found. This study has not been written yet")
            return None

        with h5py.File(self.path, "r") as fopen:
            features = get_1d_dataset(fopen, "bioturing/features")
            return [x.decode() for x in features]


    @property
    def barcodes(self) -> Union[List[str], None]:
        if self.__expression_data:
            return self.__expression_data.barcodes

        if not self.exists:
            print("WARNING: No matrix.hdf5 found. This study has not been written yet")
            return None

        with h5py.File(self.path, "r") as fopen:
            barcodes = get_1d_dataset(fopen, "bioturing/barcodes")
            return [x.decode() for x in barcodes]

    @property
    def feature_type(self) -> Union[List[Literal[constants.FEATURE_TYPES]], None]:
        if self.__expression_data:
            return self.__expression_data.feature_type

        if not self.exists:
            print("WARNING: No matrix.hdf5 found. This study has not been written yet")
            return None

        with h5py.File(self.path, "r") as fopen:
            h5bioturing = fopen["bioturing"]

            if not isinstance(h5bioturing, h5py.Group):
                return None

            if "feature_type" in h5bioturing.keys(): # Old study does not have feature_type
                feature_type = get_1d_dataset(fopen, "bioturing/feature_type")
                feature_type = [x.decode() for x in feature_type] # Tolerate weird shape of feature_type
            else :
                print("WARNING: This study does not contain info for feature type")
                features = get_1d_dataset(fopen, "bioturing/features")
                features = [x.decode() for x in features]
                feature_type = [self.detect_feature_type(x) for x in features]
        return feature_type

    @property
    def raw_matrix(self) -> Union[sparse.csc_matrix, None]:
        if self.__expression_data:
            return self.__expression_data.raw_matrix

        if not self.exists:
            print("WARNING: No matrix.hdf5 found. This study has not been written yet")
            return None

        with h5py.File(self.path, "r") as fopen:
            mtx = read_sparse_mtx(fopen, "bioturing")

        return mtx


    @property
    def norm_matrix(self) -> Union[sparse.csc_matrix, None]:
        if self.__expression_data:
            return self.__expression_data.norm_matrix

        if not self.exists:
            print("WARNING: No matrix.hdf5 found. This study has not been written yet")
            return None

        with h5py.File(self.path, "r") as fopen:
            mtx = read_sparse_mtx(fopen, "normalizedT")

        return mtx.T.tocsc()


    @staticmethod
    def detect_feature_type(feature: str) -> constants.FEATURE_TYPES:
        prefix = feature.split("-")[0]
        if prefix in get_args(constants.FEATURE_TYPES):
            return prefix  # type: ignore
        return "RNA"


    @staticmethod
    def normalize_expression(raw_matrix: sparse.csc_matrix) -> sparse.csc_matrix:
        adata = anndata.AnnData(raw_matrix)
        sc.pp.normalize_total(adata, target_sum=1e4)
        return adata.X  # type: ignore

    def add_expression_data(self, raw_matrix: Union[sparse.csc_matrix, sparse.csr_matrix],
                            barcodes: List[str],
                            features: List[str],
                            norm_matrix: Union[sparse.csc_matrix, sparse.csr_matrix, None]=None,
                            feature_type: Union[List[constants.FEATURE_TYPES], None]=None):
        if self.exists:
            print("WARNING: This study already exists, cannot add expression data")
            return None
        if not len(set(features)) == len(features):
            raise ValueError("Please make sure `features` contains no duplicates")

        raw = raw_matrix.tocsc()

        if norm_matrix is None:
            norm = self.normalize_expression(raw)
        else:
            norm = norm_matrix.tocsc()

        if feature_type is None:
            feature_type = [self.detect_feature_type(x) for x in features]

        self.__expression_data = ExpressionData(raw_matrix = raw,
                                                norm_matrix = norm,
                                                barcodes = barcodes,
                                                features = features,
                                                feature_type = feature_type)


    def write(self) -> bool:
        if self.__expression_data is None:
            print("WARNING: Expression data has not been assigned")
            return False
        if self.exists:
            print("WARNING: matrix.hdf5 has been written, cannot overwrite")
            return False


        if self.raw_matrix is None:
            return False

        if self.norm_matrix is None:
            return False

        matrix = self.raw_matrix
        with h5py.File(self.path, "w") as out_file:
            write_sparse_matrix(out_file, "bioturing", matrix=matrix, barcodes=self.barcodes,
                                    features=self.features, feature_type=self.feature_type,
                                    chunks=(min(10000, len(matrix.data)), ))

            colsum = out_file.create_group("colsum")
            write_array(colsum, "raw", np.array(matrix.sum(axis=0))[0])

            matrix = matrix.transpose().tocsc() # Sparse matrix have to be csc (legacy)
            write_sparse_matrix(out_file, key="countsT", matrix=matrix, barcodes=self.features,
                                    features=self.barcodes, chunks=(min(10000, len(matrix.data)), ))

            # log2 of just non-zeros
            matrix.data = np.log2(matrix.data + 1)

            # Sum of rows for transposed mat
            write_array(colsum, "log", np.array(matrix.sum(axis=1).reshape(-1))[0])
            norm_matrix = self.norm_matrix
            write_array(colsum, "lognorm", np.array(norm_matrix.sum(axis=0))[0])
            matrix = norm_matrix.transpose().tocsc() # Sparse matrix have to be csc (legacy)
            write_sparse_matrix(out_file, "normalizedT", matrix=matrix, barcodes=self.features,
                                    features=self.barcodes, chunks=(min(10000, len(matrix.data)), ))

        return True

def write_sparse_matrix(f, key, matrix, barcodes, features, feature_type=None, **kwargs):
    """Write sparse matrix a` la BioTuring format"""

    group = f.create_group(key)
    write_array(group, "data", matrix.data, **kwargs)
    write_array(group, "indices", matrix.indices, **kwargs)
    write_array(group, "indptr", matrix.indptr)
    write_list(group, "barcodes", barcodes)
    write_list(group, "features", features)
    write_list(group, "shape", [matrix.shape[0], matrix.shape[1]])
    if feature_type:
        write_list(group, "feature_type", feature_type)

def write_array(f, key, value, **kwargs):
    if value.dtype.kind in {"U", "O"}:
        # A` la anndata, will fail with compound dtypes
        value = value.astype(h5py.special_dtype(vlen=str))
    f.create_dataset(key, data=value, **kwargs)

def write_list(f, key, value, **kwargs):
    write_array(f, key, np.array(value), **kwargs)
