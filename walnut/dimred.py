import os
from walnut import common
from walnut.converters import IOMetaDimred, IOSingleDimred
from walnut.FileIO import FileIO
from walnut.readers import Reader, TextReader
from walnut.models import SingleDimred, SingleDimredBase, MetaDimred
import pydantic
from pydantic import validate_arguments
from typing import List, Dict, Optional
import pandas as pd

class Dimred:

	def __init__(self, dimred_folder: str, file_reader: Reader=TextReader()):
		"""
		Args:
			dimred_folder (str): "GSE111111/main/dimred" or GSE11111/sub/[sub_id]/dimred
		"""
		self.__dir = dimred_folder
		self.__file_reader = file_reader
		self.__meta: MetaDimred = MetaDimred()
		self.__dimreds: Dict[str, SingleDimred] = {}

		try:
			self.read()
		except Exception as e:
			print("WARNING: Unable to initialize dimred", common.exc_to_str(e))

	def read(self) -> None:

		if self.__get_meta_io().exists():
			self.__meta = self.__get_meta_io().read()

		self.__read_dimreds()

		self.__purge_invalid_dimreds()

	def write(self) -> None:
		self.__get_meta_io().write(self.__meta)

		for dimred_id in self.__dimreds:
			io = self.__get_single_dimred_io(dimred_id)
			single_dimred = self.__dimreds[dimred_id]
			io.write(single_dimred)


	def __read_dimreds(self):
		for dimred_id in self.__meta.get_dimred_ids():
			try:
				dimred_io = self.__get_single_dimred_io(dimred_id)
				single_dimred = dimred_io.read()

				# Skip multislide dimred
				if not single_dimred.is_multislide:
					self.__dimreds[dimred_id] = single_dimred


			except pydantic.ValidationError as e:
				print("WARNING: Unable to parse category %s due to error: %s"
						% (dimred_id, str(e)))
			except Exception as e:
				print("WARNING: Unable to read category %s due to error: %s"
						% (dimred_id, str(e)))


	def __get_meta_io(self) -> FileIO[MetaDimred]:
		return FileIO[MetaDimred](self.__get_meta_path(),
									reader=self.__file_reader,
									converter=IOMetaDimred)

	def __get_single_dimred_io(self, dimred_id: str) -> FileIO[SingleDimred]:
		return FileIO[SingleDimred](self.__get_single_dimred_path(dimred_id),
										reader=self.__file_reader,
										converter=IOSingleDimred)

	def __get_meta_path(self) -> str:
		return os.path.join(self.__dir, "meta")

	def __get_single_dimred_path(self, dimred_id: str) -> str:
		return os.path.join(self.__dir, dimred_id)

	@property
	def ids(self) -> List[str]:
		return [x for x in self.__dimreds.keys()]

	@property
	def names(self) -> List[str]:
		return [x.name for x in self.__dimreds.values()]

	@property
	def omics(self) -> List[str]:
		return [x.param.omics for x in self.__dimreds.values()]

	@property
	def sizes(self) -> List[List[int]]:
		return [x.size for x in self.__dimreds.values()]

	@validate_arguments
	def add(self, new_dimred: SingleDimred):
		single_dimred = new_dimred.copy()

		if single_dimred.id:
			dimred_id = single_dimred.id
		else:
			dimred_id = common.create_uuid()
			single_dimred.id = dimred_id

		if dimred_id in self.ids:
			print("WARNING: id % s already exists, please use another one or leave id slot empty" % dimred_id)
			return None

		dimred_meta = SingleDimredBase(**single_dimred.dict())

		self.__meta.add_dimred(dimred_meta)

		self.__dimreds[dimred_id] = single_dimred
		return dimred_id

	def remove(self, dimred_id):
		if not dimred_id in self.ids:
			print("% s dimred not found" % dimred_id)
			return False

		self.__meta.remove_dimred(dimred_id)
		del self.__dimreds[dimred_id]

		if dimred_id == self.__meta.default:
			self.__meta.default = None

		return True

	def __purge_invalid_dimreds(self) -> None:

				existing_dimreds_id = [x for x in self.__dimreds]

				# This will also delete multislide dimred, skipped for now
				# for invalid_dimred_id in numpy.setdiff1d(self.__meta.get_dimred_ids(),
				# 																						existing_dimreds_id):
				# 		print("WARNING: Removing invalid dimred %s in metalist"
				# 						% invalid_dimred_id)
				# 		self.__meta.remove_dimred(invalid_dimred_id)

				default_dimred = self.__meta.default
				if default_dimred and not default_dimred in existing_dimreds_id:
						print("WARNING: Default dimred %s not found"
										% default_dimred)
						self.__meta.default = None

	def __getitem__(self, item):
		return self.__dimreds[item]


	def __repr__(self):
		return repr(pd.DataFrame({"IDs":self.ids, "Names": self.names, "Shape": self.sizes, "Omics": self.omics}))

	def __iter__(self):
		self.__max = len(self.ids) - 1
		self.__n = 0
		return self

	def __next__(self):
		if self.__n <= self.__max:
			key = self.ids[self.__n]
			self.__n += 1
			return key
		else:
			raise StopIteration