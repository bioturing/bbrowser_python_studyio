from typing import Union, List, Literal
import os
import h5py
import pandas as pd
import numpy as np
from scipy import sparse
import scanpy as sc
import anndata
from walnut.models import ExpressionData
from walnut import constants

class Expression:
    def __init__(self, h5path):
        self.path = h5path
        self.__expression_data = None

    def __read_expression_data(self):
        if not self.exists:
            print("WARNING: No matrix.hdf5 found. This study has not been written yet")
            return None

        with h5py.File(self.path, "r") as fopen:
            data = fopen["bioturing/data"][:]
            i = fopen["bioturing/indices"][:]
            p = fopen["bioturing/indptr"][:]
            shape = fopen["bioturing/shape"][:]
            barcodes = [x.decode() for x in fopen["bioturing/barcodes"][:]]
            features = [x.decode() for x in fopen["bioturing/features"][:]]

            if "feature_type" in fopen["bioturing"].keys(): # Old study does not have feature_type
                feature_type = [x.decode() for x in fopen["bioturing/feature_type"][:].flatten()] # Tolerate weird shape of feature_type
            else :
                print("WARNING: This study does not contain info for feature type")
                feature_type = [self.detect_feature_type(x) for x in features]

        raw_matrix = sparse.csc_matrix(
                (data, i, p),
                shape=shape
            )

        with h5py.File(self.path, "r") as fopen:
            data = fopen["normalizedT/data"][:]
            i = fopen["normalizedT/indices"][:]
            p = fopen["normalizedT/indptr"][:]
            shape = fopen["normalizedT/shape"][:]

        norm_matrix = sparse.csc_matrix(
                (data, i, p),
                shape=shape
            ).T.tocsc()
        self.__expression_data = ExpressionData(raw_matrix=raw_matrix,
                                                norm_matrix=norm_matrix,
                                                barcodes = barcodes,
                                                features = features,
                                                feature_type=feature_type)


    @property
    def exists(self) -> bool:
        return os.path.isfile(self.path)


    @property
    def features(self) -> Union[List[str], None]:
        if not self.__expression_data:
            self.__read_expression_data()

        if not self.__expression_data:
            return None

        return self.__expression_data.features


    @property
    def barcodes(self) -> Union[List[str], None]:
        if not self.__expression_data:
            self.__read_expression_data()

        if not self.__expression_data:
            return None

        return self.__expression_data.barcodes


    @property
    def feature_type(self) -> Union[List[Literal[constants.FEATURE_TYPES]], None]:
        if not self.__expression_data:
            self.__read_expression_data()

        if not self.__expression_data:
            return None

        return self.__expression_data.feature_type


    @property
    def raw_matrix(self) -> sparse.csc_matrix:
        if not self.__expression_data:
            self.__read_expression_data()

        if not self.__expression_data:
            return None

        return self.__expression_data.raw_matrix


    @property
    def norm_matrix(self) -> sparse.csc_matrix:
        if not self.__expression_data:
            self.__read_expression_data()

        if not self.__expression_data:
            return None

        return self.__expression_data.norm_matrix


    @staticmethod
    def detect_feature_type(feature: str) -> Literal[constants.FEATURE_TYPES]:
        prefix = feature.split("-")[0]
        if prefix in constants.FEATURE_TYPES:
            return prefix
        return "RNA"


    @staticmethod
    def normalize_expression(raw_matrix: sparse.csc_matrix) -> sparse.csc_matrix:
        adata = anndata.AnnData(raw_matrix)
        sc.pp.normalize_total(adata, target_sum=1e4)
        return adata.X

    def add_expression_data(self, raw_matrix: Union[sparse.csc_matrix, sparse.csr_matrix],
                            barcodes: List[str],
                            features: List[str],
                            norm_matrix: Union[sparse.csc_matrix, sparse.csr_matrix]=None,
                            feature_type: List[str]=None):
        if self.exists:
            print("WARNING: This study already exists, cannot add expression data")
            return None
        if not len(set(features)) == len(features):
            raise ValueError("Please make sure `features` contains no duplicates")

        if norm_matrix is None:
            norm_matrix = self.normalize_expression(raw_matrix)
        if feature_type is None:
            feature_type = [self.detect_feature_type(x) for x in features]

        self.__expression_data = ExpressionData(raw_matrix=raw_matrix,
                                                norm_matrix=norm_matrix,
                                                barcodes = barcodes,
                                                features = features,
                                                feature_type=feature_type)


    def write(self) -> bool:
        if self.__expression_data is None:
            print("WARNING: Expression data has not been assigned")
            return False
        if self.exists:
            print("WARNING: matrix.hdf5 has been written, cannot overwrite")
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
