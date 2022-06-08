import os
import tempfile
import json
from typing import Text

from walnut.metadata import Metadata
from walnut.models import Category
from walnut.readers import TextReader
from walnut import common
meta_folder = tempfile.mkdtemp()

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
    print("Content", meta.get_content_by_id("abc"))
    assert len(meta.get_content_by_id("abc").clusterName) == 2
    assert meta.get_content_by_id("abc").clusterName == ["Unassigned", "New_cluster"]
    assert len(meta.get_content_by_id("abc").clusterLength) == 2
    assert meta.get_content_by_id("abc").clusterLength == [4, 2]
    assert meta.get_content_by_id("abc").clusters == [0, 1, 0, 1, 0, 0]

    # Append to old cluster
    meta.add_label("abc", "New_cluster", [5])
    meta = Metadata(meta_folder, TextReader())
    print("\nContent 2", meta.get_content_by_id("abc"))
    assert len(meta.get_content_by_id("abc").clusterName) == 2
    assert meta.get_content_by_id("abc").clusterName == ["Unassigned", "New_cluster"]
    assert len(meta.get_content_by_id("abc").clusterLength) == 2
    assert meta.get_content_by_id("abc").clusterLength == [3, 3]
    assert meta.get_content_by_id("abc").clusters == [0, 1, 0, 1, 0, 1]

def test_update_metadata():
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
    meta.update_metadata("abc", Category.parse_obj({"id": "abc", "name": "new_test", "type": "category", 
                                                    "clusters": [0, 0, 1, 1, 0, 1], "clusterName": ["Unassigned", "New_cluster"],
                                                    "clusterLength": [3, 3]}))
    meta = Metadata(meta_folder, TextReader())
    content = meta.get_content_by_id("abc")
    assert content.name == "new_test"
    assert content.clusters == [0, 0, 1, 1, 0, 1]
    assert content.clusterName == ["Unassigned", "New_cluster"]
    assert content.clusterLength == [3, 3]

def test_add_metadata():
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