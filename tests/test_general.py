from walnut.common import FuzzyDict
import tempfile
from walnut.study import Study

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

def test_run_info():
    study_folder = tempfile.mkdtemp()
    study = Study(study_folder)
    
    study.run_info.write()
    assert study.run_info.get("species") == "human"
    study.run_info.read()
    assert study.run_info.get("species") == "human"
