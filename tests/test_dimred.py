import sys
import os
import json
import tempfile
from fastapi.testclient import TestClient
from walnut.dimred import SingleDimred, Dimred
from walnut.readers import TextReader
# %%
def test_existing_dimred():
  tmp_dir = tempfile.mkdtemp()
  # Writing fake data
  with open(os.path.join(tmp_dir, 'meta'), "w") as fopen:
    fopen.write(json.dumps(META))

  with open(os.path.join(tmp_dir, DIMRED['id']), "w") as fopen:
    fopen.write(json.dumps(DIMRED))

  # Testing on dimred folder with existing data
  dimred = Dimred(tmp_dir, TextReader())
  _id = dimred.ids[0]
  single = dimred[_id]
  
  dimred.add(single.raw)
  dimred.write()

  dimred.remove(_id)
  dimred.write()
  
  # Testing on empty dimred folder
  tmp_dir_2 = tempfile.mkdtemp()
  dimred2 = Dimred(tmp_dir_2, TextReader())
  assert len(dimred2.data) == 0
  dimred2.add(single.raw) 
  assert len(dimred2.data) == 1

  new_dimred = {
    'id': 'abc',
    'name': 'xyz',
    'param': {'omics': 'A very weird omics'},
    'size': [10,3],
    'coords': [[1,2], [3,4], [5,6]]
  }
  assert SingleDimred.is_valid(new_dimred)

  new_dimred_2 = {
    'id': 'abc',
    # 'name': 'xyz',
    'param': {'omics': 'A very weird omics'},
    'size': [10,3],
    'coords': [[1,2], [3,4], [5,6]]
  }
  assert not SingleDimred.is_valid(new_dimred_2)
  
  dimred2.add(new_dimred)
  assert len(dimred2.data) == 2
  

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
    'seed': 2409}}},
  'version': 2,
  'bbrowser_version': '1.0.0',
  'default': 'a49318ce18434574ab922ddfad19f708'}

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
 'coords': [[-2, -4], [12, -22], [-12, 37]]}
