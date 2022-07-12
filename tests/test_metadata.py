import os
import tempfile
import json
from typing import Text

from walnut.metadata import Metadata
from walnut.models import Category
from walnut.readers import TextReader
from walnut import common
meta_folder = tempfile.mkdtemp()

def test_load_single_category():
    with open(os.path.join(meta_folder, "metalist.json"), "w") as fopen:
        json.dump({"abc": {
            "name": "test",
            "id": "abc",
            "type": "category",
            "clusterName": ["Unassigned"],
            "clusterLength": [6],
            "history": [{"created_by": "walnut", "created_at": 123, "description": "test", "hash_id": "abcde"}]
        }}, fopen)
    with open(os.path.join(meta_folder, "abc.json"), "w") as fopen:
        json.dump({
            "name": "test",
            "id": "abc",
            "type": "category",
            "clusters": [0, 0, 0, 0, 0, 0],
            "clusterName": ["Unassigned"],
            "clusterLength": [6],
            "history": [{"created_by": "walnut", "created_at": 123, "description": "test", "hash_id": "abcde"}]
        }, fopen) 
    
    meta = Metadata(meta_folder, TextReader())
    meta.read()
    assert meta.length == 1
    assert meta.get('abc').size == 6
    dfs = meta.to_df().shape
    assert dfs[0] == 6
    assert dfs[1] == 1

def test_version_0(): # no type, no history, no id
    with open(os.path.join(meta_folder, "metalist.json"), "w") as fopen:
        json.dump({"abc": {"name": "test", "clusterName": ["Unassigned"], "clusterLength": [3]}}, fopen)
    with open(os.path.join(meta_folder, "abc.json"), "w") as fopen:
        json.dump([0, 0, 0], fopen)
    
    meta = Metadata(meta_folder, TextReader())

    assert meta.to_df().index.size == 3

def test_version_1():
    with open(os.path.join(meta_folder, "metalist.json"), "w") as fopen:
        json.dump({"abc": {
            "name": "test",
            "id": "abc",
            "type": "category",
            "clusterName": ["Unassigned"],
            "clusterLength": [3],
            "history": [{"created_by": "walnut", "created_at": 123, "description": "test", "hash_id": "abcde"}]
        }}, fopen)
    with open(os.path.join(meta_folder, "abc.json"), "w") as fopen:
        json.dump({
            "name": "test",
            "id": "abc",
            "type": "category",
            "clusters": [0, 0, 0],
            "clusterName": ["Unassigned"],
            "clusterLength": [3],
            "history": [{"created_by": "walnut", "created_at": 123, "description": "test", "hash_id": "abcde"}]
        }, fopen)
    
    meta = Metadata(meta_folder, TextReader())
    assert meta.to_df().index.size == 3

def test_write_file():
    with open(os.path.join(meta_folder, "metalist.json"), "w") as fopen:
        json.dump({"abc": {
            "name": "test",
            "id": "abc",
            "type": "category",
            "clusterName": ["Unassigned"],
            "clusterLength": [6],
            "history": [{"created_by": "walnut", "created_at": 123, "description": "test", "hash_id": "abcde"}]
        }}, fopen)
    with open(os.path.join(meta_folder, "abc.json"), "w") as fopen:
        json.dump({
            "name": "test",
            "id": "abc",
            "type": "category",
            "clusters": [0, 0, 0, 0, 0, 0],
            "clusterName": ["Unassigned"],
            "clusterLength": [6],
            "history": [{"created_by": "walnut", "created_at": 123, "description": "test", "hash_id": "abcde"}]
        }, fopen)
    
    # Create new cluster
    meta = Metadata(meta_folder, TextReader())
    meta.add_label("abc", "New_cluster", [1, 3])
    meta = Metadata(meta_folder, TextReader())
    assert meta.get("abc").size == 6
    arr = meta.get("abc")
    assert arr[arr == "New_cluster"].size == 2

    # # Append to old cluster
    meta.add_label("abc", "New_cluster", [5])
    meta = Metadata(meta_folder, TextReader())
    arr = meta.get("abc")
    assert arr[arr == "New_cluster"].size == 3

def test_add_metadata_0():
    common.clear_folder(meta_folder)
    meta = Metadata(meta_folder, TextReader())

    # Create a new metadata
    id = meta.add_category("test", ["a", "a", "b"])
    cate = meta.get_content_by_id(id)
    assert len(cate.clusterName) == 3
    assert cate.type == "category"

    # Add a weird metadata
    success = True
    try:
        meta.add_category("test2", [1, 2, 3, 4])
    except:
        success = False
    assert not success

    # Add numeric-able metadata
    id = meta.add_category("test2", ["0", "1", "2"])
    cate = meta.get_content_by_id(id)
    assert cate.type == "numeric"

    # Add numeric-able metadata as category
    id = meta.add_category("test3", ["0", "1", "2"], type="category")
    cate = meta.get_content_by_id(id)
    assert cate.type == "category"

    # Sort label by clusterLength
    id = meta.add_category("test4", ["b", "a", "a"])
    cate = meta.get_content_by_id(id)
    assert cate.clusterName[1] == "a"

    # Add numeric with None
    id = meta.add_category("test5", [2, None, 1], type="numeric")

def test_add_metadata_with_len_check():
    with open(os.path.join(meta_folder, "metalist.json"), "w") as fopen:
        json.dump({"abc": {
            "name": "test",
            "id": "abc",
            "type": "numeric",
            "history": [{"created_by": "walnut", "created_at": 123, "description": "test", "hash_id": "abcde"}]
        }}, fopen)
    with open(os.path.join(meta_folder, "abc.json"), "w") as fopen:
        json.dump({
            "name": "test",
            "id": "abc",
            "type": "numeric",
            "clusters": [0, 1, 0.4, 2, 3.1, 5.2],
            "history": [{"created_by": "walnut", "created_at": 123, "description": "test", "hash_id": "abcde"}]
        }, fopen)
    
    meta = Metadata(meta_folder, TextReader())
    assert meta.get('abc').size == 6
    meta_id = meta.add_category('test 2', ['a', 'c', 'b', 'c', 'a', 'b'])
    assert meta.get(meta_id).size == 6
