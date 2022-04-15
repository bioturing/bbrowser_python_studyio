from walnut.common import FuzzyDict
from walnut.readers import TextReader
import json
import tempfile
import os

def test_fuzzy_dict():
    x = FuzzyDict({"a": 1, "b": 2})
    val = x.get("A", "a")
    assert val == 1
    val = x.get("B")
    assert val is None

def test_history():
    from walnut.models.history import History
    h = History.parse_obj({"created_by": "walnut", "created_at": 123, "hash_id": "acbs", "message": "test"})
    assert h.description == "test"

def test_run_info_0():
    from walnut.run_info import RunInfo
    study_folder = tempfile.mkdtemp()
    run_info_path = os.path.join(study_folder, "run_info.json")
    with open(run_info_path, "w") as fopen:
        json.dump({
            "study_id": "test",
            "name": "test",
            "n_samples": 123,
            "index_type": "mouse",
        }, fopen)

    run_info = RunInfo(run_info_path, TextReader())
    run_info.read()
    assert run_info.get_species() == "mouse"
