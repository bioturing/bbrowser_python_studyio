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