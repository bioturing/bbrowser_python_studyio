import pydantic
import sys
import os
import json
import tempfile
from fastapi.testclient import TestClient
from walnut.dimred import  Dimred
from walnut.dimred import SingleDimred
from walnut.readers import TextReader

# %%

def test_add_dimred():
	from walnut.study import Study
	import pandas as pd
	import numpy as np

	study_folder = tempfile.mkdtemp()
	study = Study(study_folder)
	print(study.dimred)
	coords = [[-2, -4], [12, -22], [-12, 37]]
	name ='new dimred'
	print(study.add_dimred(pd.DataFrame(coords), name))
	print(study.add_dimred(np.array(coords), name))
	print(study.add_dimred(np.array(coords), name, id='user_created_id'))
	print(study.add_dimred(np.array(coords), name, id='user_created_id'))
	try:
		study.add_dimred(coords, name)
	except ValueError as e:
		print('Could not add unformatted coords')
	print(study.dimred)

def test_dimred_model():
	dimred = SingleDimred(**DIMRED)
	dimred2 = SingleDimred(**DIMRED_MULTISLIDE)
	assert not dimred.is_multislide
	assert dimred2.is_multislide


def test_existing_dimred():
	tmp_dir = tempfile.mkdtemp()
	# Writing fake data
	with open(os.path.join(tmp_dir, 'meta'), "w") as fopen:
		fopen.write(json.dumps(META))

	with open(os.path.join(tmp_dir, DIMRED['id']), "w") as fopen:
		fopen.write(json.dumps(DIMRED))

	# Testing on dimred folder with existing data
	dimred = Dimred(tmp_dir, TextReader())
	print(dimred)
	_id = dimred.ids[0]
	single = dimred[_id]

	dimred.add(single)
	dimred.write()

	dimred.remove(_id)
	dimred.write()

	# Testing on empty dimred folder
	tmp_dir_2 = tempfile.mkdtemp()
	dimred2 = Dimred(tmp_dir_2, TextReader())
	assert len(dimred2.ids) == 0
	dimred2.add(single)
	assert len(dimred2.ids) == 1

	new_dimred = {
		'id': 'abc',
		'name': 'xyz',
		'param': {'omics': 'ADT'},
		'size': [10,3],
		'coords': [[1.5,2.1], [3.2,4.3], [5,6]]
	}
	SingleDimred(**new_dimred)

	new_dimred_2 = {
		'id': 'abc',
		# 'name': 'xyz',
		'param': {'omics': 'PRTB'},
		'size': [10,3],
		'coords': [[1.5,2.1], [3.2,4.3], [5,6]]
	}
	try:
		SingleDimred(**new_dimred_2)
	except pydantic.ValidationError as e:
		pass
	print(dimred2)
	dimred2.add(new_dimred)
	del new_dimred['id']
	assert len(dimred2.ids) == 2


	dimred2.add(new_dimred)
	dimred2.add(new_dimred)
	dimred2.add(new_dimred)
	print(dimred2)

def test_dimred_iterable():
	new_dimred = {
		# 'id': 'abc',
		'name': 'xyz',
		'param': {'omics': 'RNA'},
		'size': [10,3],
		'coords': [[1.5,2.1], [3.2,4.3], [5,6]]
	}
	tmp_dir_2 = tempfile.mkdtemp()
	dimred2 = Dimred(tmp_dir_2, TextReader())
	dimred2.add(new_dimred)
	dimred2.add(new_dimred)
	dimred2.add(new_dimred)
	print(dimred2)
	for dim in dimred2:
		print(dimred2[dim])


META = {'data': {'a49318ce18434574ab922ddfad19f708': {'id': 'a49318ce18434574ab922ddfad19f708',
	 'name': 't-SNE',
	 'size': [3, 2],
	 'history': [{'created_by': 'abc@xyz.com',
		 'created_at': 1648786133023.62,
		 'hash_id': '184c8c5e73b64bb7a237e23b5064da1c',
		 'description': 'Created with BioTuring Browser'}],
	 'param': {'omics': 'RNA',
		'dims': 2,
		'perplexity': 30,
		'method': 'tsne',
		'correction': 'none',
		'seed': 2409}},

		'abc': {'id': 'abc', # Invalid SingleDimredBase that should be purged
					'name': 't-SNE',
					'size': [3, 2],
					'history': [{'created_by': 'abc@xyz.com',
						'created_at': 1648786133023.62,
						'hash_id': '184c8c5e73b64bb7a237e23b5064da1c',
						'description': 'Created with BioTuring Browser'}],
					'param': {'omics': 'RNA',
						'dims': 2,
						'perplexity': 30,
						'method': 'tsne',
						'correction': 'none',
						'seed': 2409}}}, #
	'version': 2,
	'bbrowser_version': '1.0.0',
	'default': 'xyz'} #invalid default that will be deleted

DIMRED = {'id': 'a49318ce18434574ab922ddfad19f708',
 'name': 't-SNE',
 'size': [3, 2],
 'history': [{'created_by': 'abc@xyz.com',
	 'created_at': 1648786133023.62,
	 'hash_id': '184c8c5e73b64bb7a237e23b5064da1c',
	 'description': 'Created with BioTuring Browser'}],
 'param': {'omics': 'RNA',
	'dims': 2,
	'perplexity': 30,
	'method': 'tsne',
	'correction': 'none',
	'seed': 2409},
 'coords': [[1.5,2.1], [3.2,4.3], [5,6]]
 }

DIMRED_MULTISLIDE = {'id': 'multislide',
 'name': 't-SNE',
 'size': [3, 2],
 'param': {'omics': 'RNA',
	'dims': 2,
	'perplexity': 30,
	'method': 'tsne',
	'correction': 'none',
	'seed': 2409},
	'slide': ['slide1', 'slide2']
 }
