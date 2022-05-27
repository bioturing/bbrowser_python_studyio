import os
import tempfile
import json

from walnut.metadata import Metadata
from walnut.graphcluster import GraphCluster
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

def test_graph_cluster_v1():
    position = 'root'
    study_path = "C:/Users/milan/.BioTBDataDev/Data/SingleCell/Study/harris2018"
    sub_cluster = GraphCluster(position=position, study_folder=study_path, reader=TextReader())
    selection = [0, 1, 2]
    print("Sub cluster:", sub_cluster.convert_to_main_cluster(selection))
    assert len(sub_cluster.convert_to_main_cluster(selection)) > 0