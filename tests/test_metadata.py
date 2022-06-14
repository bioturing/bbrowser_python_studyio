import os
import tempfile
import json

from walnut.metadata import Metadata
from walnut.converters import IOCategory
from walnut.readers import TextReader
from walnut.graphcluster import GraphCluster
from walnut.common import create_history

study_dir = tempfile.mkdtemp()
os.mkdir(os.path.join(study_dir, "main"))
os.mkdir(os.path.join(study_dir, "main", "metadata"))
meta_folder = os.path.join(study_dir, "main", "metadata")

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
    assert len(meta.get_content_by_id("abc").clusterName) == 2
    assert meta.get_content_by_id("abc").clusterName == ["Unassigned", "New_cluster"]
    assert len(meta.get_content_by_id("abc").clusterLength) == 2
    assert meta.get_content_by_id("abc").clusterLength == [4, 2]
    assert meta.get_content_by_id("abc").clusters == [0, 1, 0, 1, 0, 0]

    # Append to old cluster
    meta.add_label("abc", "New_cluster", [5])
    meta = Metadata(meta_folder, TextReader())
    assert len(meta.get_content_by_id("abc").clusterName) == 2
    assert meta.get_content_by_id("abc").clusterName == ["Unassigned", "New_cluster"]
    assert len(meta.get_content_by_id("abc").clusterLength) == 2
    assert meta.get_content_by_id("abc").clusterLength == [3, 3]
    assert meta.get_content_by_id("abc").clusters == [0, 1, 0, 1, 0, 1]

def test_update_metadata_1():
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
    metadata_json = '{"id": "abc", "name": "new_test", "type": "category",\
                                                    "clusters": [0, 0, 1, 1, 0, 1], "clusterName": ["Unassigned", "New_cluster"],\
                                                    "clusterLength": [3, 3]}'
    meta.update_metadata("abc", IOCategory.from_str(metadata_json))
    meta = Metadata(meta_folder, TextReader())
    content = meta.get_content_by_id("abc")
    assert content.name == "new_test"
    assert content.clusters == [0, 0, 1, 1, 0, 1]
    assert content.clusterName == ["Unassigned", "New_cluster"]
    assert content.clusterLength == [3, 3]

def test_update_metadata_2():
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
    
    sub_dir = os.path.join(study_dir, "sub")
    os.makedirs(os.path.join(sub_dir, "abc"), exist_ok=True)
    cl_file = os.path.join(sub_dir, "abc", "cluster_info.json")
    with open(cl_file, "w") as fopen:
        json.dump({
            "id": "abc",
            "name": "test",
            "history": [create_history().dict()],
            "length": 4,
            "version": 2,
            "parent_id": "root",
            "img": "",
            "selectedArr": [1, 2, 4, 5]
        }, fopen)

    sub_cluster = GraphCluster("abc", sub_dir, TextReader())
    meta = Metadata(meta_folder, TextReader())
    metadata_json = '{"id": "abc",  "name": "new_test", "type": "category",\
                                                    "clusters": [1, 1, 1, 0], "clusterName": ["Unassigned", "New_cluster"],\
                                                    "clusterLength": [3, 3]}'
    meta.update_metadata("abc", IOCategory.from_str(metadata_json), sub_cluster.get_selected_arr())
    meta = Metadata(meta_folder, TextReader())
    content = meta.get_content_by_id("abc")
    assert content.name == "new_test"
    assert content.clusters == [0, 1, 1, 0, 1, 0]
    assert content.clusterName == ["Unassigned", "New_cluster"]
    assert content.clusterLength == [3, 3]

def test_new_metadata_1():
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
    metadata_json = '{"id": "abc_2", "name": "new_test", "type": "category",\
                        "clusters": [0, 0, 1, 1, 0, 1], "clusterName": [],\
                                                    "clusterLength": []}'
    meta.update_metadata("abc_2", IOCategory.from_str(metadata_json, auto_fill_cluster_names=True))
    meta = Metadata(meta_folder, TextReader())
    content = meta.get_content_by_id("abc_2")
    assert content.name == "new_test"
    assert content.clusters == [0, 0, 1, 1, 0, 1]
    assert content.clusterName == ["Unassigned", "Cluster 1"]
    assert content.clusterLength == [3, 3]

def test_new_metadata_2():
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
    
    sub_dir = os.path.join(study_dir, "sub")
    os.makedirs(os.path.join(sub_dir, "abc_sub"), exist_ok=True)
    cl_file = os.path.join(sub_dir, "abc_sub", "cluster_info.json")
    with open(cl_file, "w") as fopen:
        json.dump({
            "id": "abc_sub",
            "name": "test",
            "history": [create_history().dict()],
            "length": 4,
            "version": 2,
            "parent_id": "root",
            "img": "",
            "selectedArr": [1, 2, 4, 5]
        }, fopen)

    sub_cluster = GraphCluster("abc_sub", sub_dir, TextReader())
    meta = Metadata(meta_folder, TextReader())
    metadata_json = '{"id": "abc_2",  "name": "new_test", "type": "category",\
                                                    "clusters": [1, 1, 1, 0], "clusterName": [],\
                                                    "clusterLength": []}'
    meta.update_metadata("abc_2", IOCategory.from_str(metadata_json, auto_fill_cluster_names=True), sub_cluster.get_selected_arr())
    meta = Metadata(meta_folder, TextReader())
    content = meta.get_content_by_id("abc_2")
    assert content.name == "new_test"
    assert content.clusters == [0, 1, 1, 0, 1, 0]
    assert content.clusterName == ["Unassigned", "Cluster 1"]
    assert content.clusterLength == [3, 3]