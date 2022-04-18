from walnut.common import FuzzyDict

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
