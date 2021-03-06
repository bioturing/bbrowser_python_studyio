import tempfile
import json
import os

def test_create_gene_collection():
    from walnut.study import Study
    study_folder = tempfile.mkdtemp()
    study = Study(study_folder, 'human')

    # Test initializing from json
    imm_id = study.create_gene_collection("immune", ["CD3D", "NKG7", "CD79A"])
    tcell_id = study.create_gene_collection("T cells", ["CD3D", "CD8A"])
    json_str = study.gallery.to_json()
    cfg = json.loads(json_str)
    assert len(cfg) == 2
    assert len(cfg[0]["items"]) == 3
    assert len(cfg[1]["items"]) == 2
    study.gallery.from_json(json_str)
    assert study.gallery.get(imm_id) == ['ENSG00000167286', 'ENSG00000105374', 'ENSG00000105369']
    assert study.gallery.get(tcell_id) == ['ENSG00000167286', 'ENSG00000153563']

def test_version_1():
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