import os
import tempfile
import json

from walnut.metadata import Metadata
from walnut.readers import TextReader
meta_folder = tempfile.mkdtemp()

def test_version_0(): # no type, no history, no id
    with open(os.path.join(meta_folder, "metalist.json"), "w") as fopen:
        json.dump({"abc": {"name": "test", "clusterName": ["Unassigned"], "clusterLength": [3]}}, fopen)
    with open(os.path.join(meta_folder, "abc.json"), "w") as fopen:
        json.dump([0, 1, 2], fopen)
    
    meta = Metadata(meta_folder, TextReader())
    print(meta.to_df())

def test_version_1():
    with open(os.path.join(meta_folder, "metalist.json"), "w") as fopen:
        json.dump({"abc": {
            "name": "test",
            "id": "abc",
            "type": "category",
            "clusterName": ["Unassigned"],
            "clusterLength": [3],
            "history": [{"created_by": "tri@bioturing.com", "created_at": 123, "description": "test", "hasd_id": "abcde"}]
        }}, fopen)
    with open(os.path.join(meta_folder, "abc.json"), "w") as fopen:
        json.dump({
            "name": "test",
            "id": "abc",
            "type": "category",
            "clusters": [0, 1, 2],
            "clusterName": ["Unassigned"],
            "clusterLength": [3],
            "history": [{"created_by": "tri@bioturing.com", "created_at": 123, "description": "test", "hasd_id": "abcde"}]
        }, fopen)
    
    meta = Metadata(meta_folder, TextReader())
    print(meta.to_df())