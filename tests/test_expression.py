from walnut.expression import Expression
from walnut.study import Study
from walnut.models import ExpressionData
from walnut.gene_db import GeneDB
from walnut import common
import os
import scanpy as sc
import tarfile, tempfile
import json
import pathlib
import numpy as np
import scipy.sparse as sparse


# Generating fake data

tmp_dir = tempfile.mkdtemp()
n_gene = 2000
n_cell = 1000
data = sparse.random(n_cell, n_gene, density=.2, format="csr",
                 data_rvs=np.ones,   # fill with ones
                 dtype="f"           # use float32 first
                 ).astype("int8")    # then convert to int8

gene_db = GeneDB(os.path.join(common.get_pkg_data(), "db"), "human")
gene_db.read()
df = gene_db.to_df()

adata = sc.AnnData(data, dtype=data.dtype)
gene_ids = df["gene_id"][0:n_gene]


adata.var_names = gene_ids

barcodes = adata.obs_names.tolist()
features = adata.var_names.tolist()

study_path = tempfile.mkdtemp()



def test_expression_model():
    study_path = tempfile.mkdtemp()

    expression = Expression(os.path.join(study_path, "matrix.hdf5"))


    duplicated_features = gene_ids.copy()
    duplicated_features[0:100] = duplicated_features[100:200]
    assert sum(duplicated_features.duplicated()) > 0

    # Adding feature list with duplicates, should fail
    try:
        expression.add_expression_data(raw_matrix=adata.X.T, barcodes=barcodes, features=duplicated_features)
        assert 1 == 0
    except Exception as e:
        print(e)

    # Adding unique feature list with duplicates, should pass
    expression.add_expression_data(raw_matrix=adata.X.T, barcodes=barcodes, features=features)

    assert expression.write()
    assert not expression.write() # Cannot write after matrix.hdf5 already exists


def test_expression_data_model():
    feature_type = [Expression.detect_feature_type(x) for x in features]
    expression = ExpressionData(raw_matrix = adata.X.T,
                    norm_matrix = adata.X.T,
                    barcodes = barcodes,
                    features = features,
                    feature_type = feature_type)

    try:
        raw = adata.X.T
        raw = raw - raw * 2 # Creating negative values
        assert raw.min() < 0
        expression = ExpressionData(raw_matrix = raw,
                        norm_matrix = adata.X.T,
                        barcodes = barcodes,
                        features = features,
                        feature_type = feature_type)
        assert 1 == 0 # Make sure the above not work
    except ValueError as e:
        print(e)


def test_expression_existing_study():
    study_path = tempfile.mkdtemp()
    study = Study(study_path, "human")

    assert study.write_expression_data(raw_matrix=adata.X.T, barcodes=barcodes, features=features)
    assert not study.write_expression_data(raw_matrix=adata.X.T, barcodes=barcodes, features=features)
    run_info_path = os.path.join(study_path, "run_info.json")
    with open(run_info_path, "w") as fopen:
        json.dump({
            "study_id": "test",
            "name": "test",
            "n_samples": 123,
            "index_type": "human",
        }, fopen)

    # After run_info and matrix.hdf5 are created, new study should be able to init without species arg
    study = Study(study_path)

    # Remove human.db to see if Study can still be init
    db_path = os.path.join(study_path, "main/gene/human.db")
    os.remove(db_path)
    assert not os.path.isfile(db_path)
    study = Study(study_path)
    assert os.path.isfile(db_path)
    assert study.expression.raw_matrix.shape == adata.X.T.shape
    assert study.expression.norm_matrix.shape == adata.X.T.shape
    assert len(study.expression.barcodes) == len(barcodes)
    assert len(study.expression.features) == len(features)
    assert len(study.expression.feature_type) == len(features)