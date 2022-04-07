from walnut.common import FuzzyDict
import tempfile
import json
import os
from walnut.study import Study
from walnut.gene_db import GeneDB
from walnut import common

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

def test_create_gene_collection():
    from walnut.study import Study
    study_folder = tempfile.mkdtemp()
    study = Study(study_folder)

    # Test initializing from json
    imm_id = study.create_gene_collection("immune", ["CD3D", "NKG7", "CD79A"])
    tcell_id = study.create_gene_collection("T cells", ["CD3D", "CD8A"])
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

def test_gallery():
    from walnut.gallery import Gallery
    from walnut.readers import TextReader
    gallery_folder = tempfile.mkdtemp()
    with open(os.path.join(gallery_folder, "gene_gallery_2.json"), "w") as fopen:
        json.dump([{
            "name": "test",
            "type": "RNA",
            "items": [{
                "name": "test",
                "id": "test0",
                "created_at": 1234,
                "last_modified": 1234,
                "features": ["CD3D"],
            }],
            "id": "asdasd",
            "created_at": 1234,
            "last_modified": 1234,
            "created_by": "test@bioturing.com",
        }], fopen)
    
    gallery = Gallery(gallery_folder, TextReader())
    gallery.read()
    assert len(gallery.get("asdasd")) == 1

def test_run_info():
    study_folder = tempfile.mkdtemp()
    study = Study(study_folder)
    
    study.run_info.write()
    assert study.run_info.get("species") == "human"
    study.run_info.read()
    assert study.run_info.get("species") == "human"

def test_gene_db_conversion():
    gene_db = GeneDB("C:/Users/lequa/Documents/bbrowser_python_studyio/walnut/data", "human")
    gene_db.read()
    ids = gene_db.convert(["CD3D", "CD79A"])
    assert ids == ["ENSG00000167286", "ENSG00000105369"]
    names = gene_db.convert(ids, _from="gene_id", _to="name")
    assert names == ["CD3D", "CD79A"]
    assert gene_db.is_id(ids)

def test_gene_db_creation():
    study_folder = tempfile.mkdtemp()
    study = Study(study_folder)
    study.gene_db.create(["CD3D", "CD79A", "TRILE", "CCL5", "EPCAM"])
    study.gene_db.read()
    df = study.gene_db.to_df()
    assert df.index.size == 5
    db = GeneDB(common.get_pkg_data(), study.run_info.get("species"))
    db.read()
    assert db.is_id(df["gene_id"])