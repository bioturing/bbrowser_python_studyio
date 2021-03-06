import tempfile
import os
from walnut.gene_db import GeneDB
from walnut.study import Study
from walnut import common

def test_gene_db_conversion():
    gene_db = GeneDB(os.path.join(common.get_pkg_data(), 'db'), "human")
    gene_db.read()
    ids = gene_db.convert(["CD3D", "CD79A"])
    assert ids == ["ENSG00000167286", "ENSG00000105369"]
    names = gene_db.convert(ids, _from="gene_id", _to="name")
    assert names == ["CD3D", "CD79A"]
    assert gene_db.is_id(ids)

def test_gene_db_creation():
    study_folder = tempfile.mkdtemp()
    study = Study(study_folder, 'human')
    study.gene_db.create(["CD3D", "CD79A", "TRILE", "CCL5", "EPCAM"])
    study.gene_db.read()
    df = study.gene_db.to_df()
    assert df.index.size == 5
    db = GeneDB(os.path.join(common.get_pkg_data(), 'db'), study.run_info.get_species())
    db.read()
    assert db.is_id(df["gene_id"].tolist())


def test_gene_db_creation_large_data():
    # Prepare data
    
    gene_db = GeneDB(os.path.join(common.get_pkg_data(), 'db'), "human")
    gene_db.read()
    df = gene_db.to_df()
    features = df['gene_id'][0:10000]

    study_folder = tempfile.mkdtemp()
    study = Study(study_folder, 'human')
    study.gene_db.create(features.tolist())
    study.gene_db.read()
    df = study.gene_db.to_df()
    assert sum(df['gene_id'].duplicated()) == 0
    assert df.index.size == len(features)
    db = GeneDB(os.path.join(common.get_pkg_data(), 'db'), study.run_info.get_species())
    db.read()
    assert db.is_id(df["gene_id"].tolist())


