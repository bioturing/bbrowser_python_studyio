import h5py
import os
import pandas as pd
import numpy as np
from scipy import sparse
from walnut.gene_db import StudyGeneDB
from walnut.models import ExpressionData
from pydantic import validate_arguments, ValidationError
from walnut import constants, common
from typing import Union, List



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

			if "feature_type" in fopen['bioturing'].keys(): # Old study does not have feature_type
				feature_type = [x.decode() for x in fopen["bioturing/feature_type"][:].flatten()] # Tolerate weird shape of feature_type
			else :
				print('WARNING: This study does not contain info for feature type')
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
	def features(self):
		if not self.__expression_data:
			self.__read_expression_data()
		
		if not self.__expression_data:
			return None
		
		return self.__expression_data.features


	@property
	def barcodes(self):
		if not self.__expression_data:
			self.__read_expression_data()
		
		if not self.__expression_data:
			return None

		return self.__expression_data.barcodes


	@property
	def feature_type(self):
		if not self.__expression_data:
			self.__read_expression_data()
		
		if not self.__expression_data:
			return None

		return self.__expression_data.feature_type
	
	
	@property
	def raw_matrix(self):
		if not self.__expression_data:
			self.__read_expression_data()
		
		if not self.__expression_data:
			return None

		return self.__expression_data.raw_matrix
	
	
	@property
	def norm_matrix(self):
		if not self.__expression_data:
			self.__read_expression_data()
		
		if not self.__expression_data:
			return None

		return self.__expression_data.norm_matrix


	@staticmethod
	def detect_feature_type(feature: str):
		prefix = feature.split('-')[0]
		if prefix in constants.FEATURE_TYPES:
			return prefix
		return 'RNA'
	
	
	@staticmethod
	def normalize_expression(raw_matrix):
		import scanpy as sc
		import anndata
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


	def write(self):
		if self.__expression_data is None:
			print("WARNING: Expression data has not been assigned")
			return False
		if self.exists:
			print("WARNING: matrix.hdf5 has been written, cannot overwrite")
			return False
		feature_type = self.__expression_data.feature_type

		barcodes = pd.DataFrame({'barcodes': self.__expression_data.barcodes})

		genes = pd.DataFrame({
				'genes': self.__expression_data.features,
				'feature_type': feature_type,
			})
		matrix = self.__expression_data.raw_matrix
		with h5py.File(self.path, "w") as out_file:
			group = out_file.create_group('bioturing')
			group.create_dataset('barcodes', data=barcodes['barcodes'].values.astype('S'))
			group.create_dataset('features', data=genes['genes'].values.astype('S'))
			group.create_dataset('data', data=matrix.data)
			group.create_dataset('indices', data=matrix.indices)
			group.create_dataset('indptr', data=matrix.indptr)
			group.create_dataset('shape', data=[matrix.shape[0], matrix.shape[1]])
			group.create_dataset('feature_type', data=genes['feature_type'].values.astype('S'))
			colsum = out_file.create_group('colsum')
			colsum.create_dataset('raw', data=np.array(matrix.sum(axis=0))[0])

			matrix = matrix.transpose().tocsc() # Sparse matrix have to be csc (legacy)
			group = out_file.create_group('countsT')
			group.create_dataset('features', data=barcodes['barcodes'].values.astype('S'))
			group.create_dataset('barcodes', data=genes['genes'].values.astype('S'))
			group.create_dataset('data', data=matrix.data)
			group.create_dataset('indices', data=matrix.indices)
			group.create_dataset('indptr', data=matrix.indptr)
			group.create_dataset('shape', data=[matrix.shape[0], matrix.shape[1]])

			matrix.data = np.log2(matrix.data + 1) # log2 of just non-zeros
			colsum.create_dataset('log', data=np.array(matrix.sum(axis=1).reshape(-1))[0]) # Sum of rows for transposed mat

			norm_matrix = self.__expression_data.norm_matrix
			colsum.create_dataset('lognorm', data=np.array(norm_matrix.sum(axis=0))[0])

			matrix = norm_matrix.transpose().tocsc() # Sparse matrix have to be csc (legacy)
			group = out_file.create_group('normalizedT')
			group.create_dataset('features', data=barcodes['barcodes'].values.astype('S'))
			group.create_dataset('barcodes', data=genes['genes'].values.astype('S'))
			group.create_dataset('data', data=matrix.data)
			group.create_dataset('indices', data=matrix.indices)
			group.create_dataset('indptr', data=matrix.indptr)
			group.create_dataset('shape', data=[matrix.shape[0], matrix.shape[1]])

		return True