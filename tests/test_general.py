from walnut.common import FuzzyDict
import tempfile
import json

def test_fuzzy_dict():
    x = FuzzyDict({'a': 1, 'b': 2})
    val = x.get('A', 'a')
    assert val == 1
    val = x.get('B')
    assert val is None

def test_gallery():
    from walnut.study import Study
    study_folder = tempfile.mkdtemp()
    study = Study(study_folder)

    # Test initializing from dict
    imm_id = study.gallery.create_gene_collection("immune", ["CD3D", "NKG7", "CD79A"])
    tcell_id = study.gallery.create_gene_collection("T cells", ["CD3D", "CD8A"])
    json_str = study.gallery.to_json()
    cfg = json.loads(json_str)
    assert len(cfg) == 2
    assert len(cfg[0]["items"]) == 3
    assert len(cfg[1]["items"]) == 2
    study.gallery.from_json(json_str)
    assert len(study.gallery.get(imm_id)) == 3
    assert len(study.gallery.get(tcell_id)) == 2

    # Test initializing from file
    study.gallery.write()
    study = Study(study_folder)
    study.gallery.read()
    assert len(study.gallery.get(imm_id)) == 3
    assert len(study.gallery.get(tcell_id)) == 2
