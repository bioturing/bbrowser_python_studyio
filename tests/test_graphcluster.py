import tempfile
import os
import json
from walnut import common
from walnut.graphcluster import GraphCluster
from walnut.readers import TextReader

def test_graph_cluster_v1():
    study_dir = tempfile.mkdtemp()
    sub_dir = os.path.join(study_dir, "sub")
    os.makedirs(os.path.join(sub_dir, "abc"), exist_ok=True)
    cl_file = os.path.join(sub_dir, "abc", "cluster_info.json")
    with open(cl_file, "w") as fopen:
        json.dump({
            "id": "abc",
            "name": "test",
            "history": [common.create_history().dict()],
            "length": 3,
            "version": 2,
            "parent_id": "root",
            "img": "",
            "selectedArr": [3, 5, 7]
        }, fopen)

    sub_cluster = GraphCluster("abc", sub_dir, TextReader())
    selection = [0, 1, 2]
    main_idx = sub_cluster.convert_to_main_cluster(selection)
    assert len(main_idx) == len(selection)
    assert main_idx[0] == 3
    assert main_idx[1] == 5
    assert main_idx[2] == 7

def test_get_full_index_array():
    # TODO: Implement after writing study with subcluster
    pass