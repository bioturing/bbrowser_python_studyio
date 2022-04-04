from walnut.common import FuzzyDict

def test_fuzzy_dict():
    x = FuzzyDict({'a': 1, 'b': 2})
    val = x.get('A', 'a')
    assert val == 1
    val = x.get('B')
    assert val is None

def test_study():
    from walnut.study import Study
    study = Study('/fake_study')
    assert isinstance(study, Study)
