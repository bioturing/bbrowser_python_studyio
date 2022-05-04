import tempfile
from walnut.gene_db import GeneDB
from walnut.study import Study
from walnut import common
import os, pathlib, tarfile
import scanpy as sc

def test_gene_db_conversion():
    gene_db = GeneDB(common.get_pkg_data(), "human")
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
    db = GeneDB(common.get_pkg_data(), study.run_info.get_species())
    db.read()
    assert db.is_id(df["gene_id"])


def test_gene_db_creation_with_dup():
    # Prepare data
    current_dir = os.path.dirname(pathlib.Path(__file__))
    data_path = os.path.join(current_dir, 'test_data/pbmc3k_filtered_gene_bc_matrices.tar.gz')
    file = tarfile.open(data_path)
    tmp_dir = tempfile.mkdtemp()

    file.extractall(tmp_dir)
    file.close()

    adata = sc.read_10x_mtx(
        os.path.join(tmp_dir, 'filtered_gene_bc_matrices/hg19/'),
        var_names='gene_symbols',
        cache=True)

    features = adata.var_names.tolist()


    study_folder = tempfile.mkdtemp()
    study = Study(study_folder)
    study.gene_db.create(features)
    study.gene_db.read()
    df = study.gene_db.to_df()
    assert sum(df['gene_id'].duplicated()) == 0
    assert df.index.size == len(features)
    db = GeneDB(common.get_pkg_data(), study.run_info.get_species())
    db.read()
    assert db.is_id(df["gene_id"])


