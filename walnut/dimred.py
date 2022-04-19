import os
from walnut import common
from walnut.converters import IOJSON
from walnut.FileIO import FileIO
from walnut.readers import Reader
from walnut.models import DimredDataBasic, DimredDataMultislide
from pydantic import validator, validate_arguments
from typing import List, Union, Type
import pandas as pd

class Dimred:

	def __init__(self, dimred_folder: str, reader: Reader):
		"""
		Args:
			dimred_folder (str): 'GSE111111/main/dimred' or GSE11111/sub/[sub_id]/dimred
		"""
		self.__dir = dimred_folder
		self.__reader = reader
		self.__metalist = FileIO(os.path.join(self.__dir, "meta"), self.__reader, IOJSON)
		self.data = dict()
		self.__meta = {'data': dict()}
		self.__old_meta = {'data': dict()}
		self.ids = []
		self.__old_ids = []
		self.names = []
		if self.__metalist.exists():
			self.__read()

	def __read(self):
		"""Read dimred data from the given dir"""
		if not self.__metalist.exists():
			raise IOError("No dimred data to read")

		self.__meta = self.__metalist.read()
		self.data = dict()

		for id in self.__meta['data']:
			self.data[id] = SingleDimred(os.path.join(self.__dir, id), reader = self.__reader)

		self.ids = self.__get_ids()
		self.names = self.__get_names()
		self.__old_ids = list(self.__meta['data'].keys())

	def write(self):
		
		all_ids = set(self.ids + self.__old_ids)
		
		for id in all_ids:
			if not id in self.__old_ids:
				# New id to be added
				print("Writing %s dimred" % id)
				self.data[id].write()
			
			if not id in self.ids:
				# Old id to be removed
				print("Removing %s dimred" % id)
				SingleDimred(os.path.join(self.__dir, id), reader=self.__reader).remove()

		self.__metalist.write(self.__meta)
		self.__old_ids = list(self.__meta['data'].keys())


	@validate_arguments
	def add(self, dimred_info: Union[DimredDataBasic, DimredDataMultislide]):
		"""Add new dimred to a study/subcluster

		Args:
			dimred_info (dict): A dictionary with obligatory keys: ['coords', 'name', 'id', 'size', 'param'], and optionally ['history'].
			Will be validated with pydantic to ensure all required slots (coords/slides, history, param, etc)
			id (_type_, optional): id of the new dimred to be written. Will be generated if not passed. 
			Dimred_info.id will be forced to be equal to id.
		"""
		id = dimred_info.id if dimred_info.id else common.create_uuid()

		if id in self.data.keys():
			print('id % s already exists, please use another one or leave id slot empty' % id)
			return None

		# Force id in dimred_info to be the same as id
		dimred_info.id = id
		out_path = os.path.join(self.__dir, id)

		dimred = SingleDimred(out_path, reader=self.__reader)
		content = dimred_info.dict()
		dimred.set_raw(content.copy())

		if 'coords' in content.keys():
			del content['coords']

		# Update `meta` content
		self.__meta['data'][id] = content

		self.data[id] = dimred

		self.ids = self.__get_ids()
		self.names = self.__get_names()

		return id

	def __get_ids(self):
		return list(self.data.keys())


	def __get_names(self):
		names = []
		for k, dimred in self.data.items():
			names.append(dimred.raw.get('name', 'Name not given'))
		return names


	def __get_shapes(self):
		shapes = []
		for k, dimred in self.data.items():
			shapes.append(dimred.raw.get('size', 'Shape not given'))
		return shapes


	def get(self, id):
		"""Get a SingleDimred object"""
		return self.data.get(id)


	def remove(self, id):
		if not id in self.data.keys():
			print("% s dimred not found" % id)
			return False
		
		out_path = os.path.join(self.__dir, id)

		dimred = SingleDimred(out_path, reader=self.__reader)
		
		del self.__meta['data'][id]
		del self.data[id]
		if id == self.__meta.get('default', 'None'):
			del self.__meta['default']
		
		self.ids = self.__get_ids()
		self.names = self.__get_names()

		return True


	def __getitem__(self, item):
		return self.get(item)


	def __repr__(self):
		""""return an overview of all dimred, id, name, type, dim"""
		shapes = self.__get_shapes()
		return repr(pd.DataFrame({'IDs':self.ids, 'Names': self.names, 'Shape': shapes}))

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

class SingleDimred:
	def __init__(self, path, reader: Reader):
		"""self.raw: raw content read from text file, 
									could also be used to store 
									new dimred info to be written to file.
		"""
		self.__json = FileIO(path, reader, IOJSON)
		self.id = os.path.basename(path)
		self.raw = dict()
		self.path = path

		if self.__json.exists():
			self.__read()

	def __read(self):
		if not self.__json.exists():
			raise IOError("No dimred found in given path % s" % self.path)
		
		dimred = self.__json.read()
		if not SingleDimred.is_valid(dimred):
			raise IOError("Not valid dimred content in given path % s" % self.path)

		self.raw = dimred
		self.__get_info()

	def write(self):
		if self.__json.exists():
			print('Another dimred file already exists at % s. Replacing ' % self.path)
		
		self.__json.write(self.raw)

	def __get_omics(self):
		return self.raw['param'].get('omics', 'NA')

	def __get_name(self):
		return self.raw.get('name', 'NA')
	
	def __get_history(self):
		return self.raw.get('history', 'No history found')
	
	def __get_param(self):
		return self.raw.get('param', 'No param found')

	def __get_coords(self):
		if self.omics == 'multislide':
			return self.raw['slide']
		else:
			return pd.DataFrame(self.raw['coords'])

	def __get_shape(self):
		self.omics = self.__get_omics()
		self.coords = self.__get_coords()
		if self.omics == 'multislide':
			return len(self.coords)
		else:
			return self.coords.shape

	def remove(self):
		self.__json.delete()

	@classmethod
	def is_valid(cls, info):
		"""Check if raw content is a valid dimred

		Args:
			info (_type_): content read from a dimred text file
		"""
		@validate_arguments
		def _check(info: Union[DimredDataMultislide, DimredDataBasic]):
			pass
		try:
			_check(info)
			return True
		except Exception as e:
			print("Not valid dimred content")
			print(common.exc_to_str(e))
			return False

	def set_raw(self, content):
		if not SingleDimred.is_valid(content):
			return
		self.raw = content
		self.__get_info()

	def __get_info(self):
		"""Generic function to make sure all slot is available after init"""
		self.omics = self.__get_omics()
		self.name = self.__get_name()
		self.history = self.__get_history()
		self.param = self.__get_param()
		self.coords = self.__get_coords()
		self.shape = self.__get_shape()

	def __getitem__(self, item):
		if not item in vars(self).keys():
			print('This object does not have `%s` slot' % item)
			return
		return getattr(self, item)

	def __repr__(self):
		return repr('`{name}` constructed from `{omics}` with shape {shape}'
					.format(name=self.name, omics=self.omics, shape=self.shape))