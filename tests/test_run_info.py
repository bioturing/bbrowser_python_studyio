from pydantic import annotated_types
from walnut.readers import TextReader
import tempfile
import os
import json
from walnut.run_info import RunInfo

def test_run_info_0():
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

# Test nanostring data
def test_run_info_1():
    study_folder = tempfile.mkdtemp()
    run_info_path = os.path.join(study_folder, "run_info.json")
    with open(run_info_path, "w") as fopen:
        json.dump({
            "study_id": "test",
            "name": "test",
            "n_samples": 123,
            "n_batch": 2,
            "index_type": "human",
            "omics": ["nanostring", "RNA"],
            "ana_setting": {"inputType": ["dsp", "dsp"]}
        }, fopen)

    run_info = RunInfo(run_info_path, TextReader())
    run_info.read()

# Test strange filter settings
def test_run_info_2():
    study_folder = tempfile.mkdtemp()
    run_info_path = os.path.join(study_folder, "run_info.json")
    with open(run_info_path, "w") as fopen:
        json.dump({
            "study_id": "test",
            "name": "test",
            "n_samples": 123,
            "index_type": "human",
            "ana_setting": {"filter": {"gene": [[200], [4000]]}}
        }, fopen)

    run_info = RunInfo(run_info_path, TextReader())
    run_info.read()

    with open(run_info_path, "w") as fopen:
        json.dump({
            "study_id": "test",
            "name": "test",
            "n_samples": 123,
            "index_type": "human",
            "ana_setting": {"filter": {"gene": 200}}
        }, fopen)
    run_info.read()

# Test MOCA2M run_info
def test_moca_run_info():
    study_folder = tempfile.mkdtemp()
    run_info_path = os.path.join(study_folder, "run_info.json")
    with open(run_info_path, "w") as fopen:
        json.dump(
                {'dimred': 'umap', 'hash_id': 'MOCA_2M', 'version': 16, 'n_cell': 1331984, 'modified_date': 1657181760882, 'addon': 'SingleCell', 
                  'matrix_type': 'single', 'ana_setting': {'dimred': {'perplexity': 5, 'method': 'tsne'}, 
                  'filter': {'gene': [200, 0], 'cell': 5, 'mito': 5, 'top': 2000}, 'batchRemoval': 'none', 'normMethod': 'none', 'refIndex': 'unknown', 
                  'quant': {'name': 'Unknown', 'version': ''}, 'inputType': ['singleMTX']}, 'n_batch': 1, 'tag': ['5f06a6976a0388790aeb7089', '5f06a6976a0388790aeb708a', '5f06a6976a0388790aeb7099'], 
                  'title': 'The single-cell transcriptional landscape of mammalian organogenesis', 'species': 'mouse', 'unit_settings': {'RNA': {'type': 'norm', 'transform': 'none'},
                  'ADT': {'type': 'norm', 'transform': 'none'}, 'PRTB': {'type': 'norm', 'transform': 'none'}}, 'platform': 'sci3', 'misc': {}, 'papers': [], 
                  'abstract': 'The single-cell transcriptional landscape of mammalian organogenesis', 'author': ['Junyue Cao', 'Malte Spielmann', 'Xiaojie Qiu', 'Xingfan Huang', 
                  'Daniel Ibrahim', 'Andrew Hill', 'Fan Zhang', 'Stefan Mundlos', 'Lena Christiansen', 'Frank Steemers', 'others'], 'unit': 'umi', 'shareTag': [], 'remote': {}, 
                  'history': [{'hash_id': 'MOCA_2M', 'created_by': 'support@bioturing.com',
                  'created_at': 1657101607588, 'description': 'Auto generated history'}], 'is_public': True, 'omics': ['RNA']}, fopen)
    run_info = RunInfo(run_info_path, TextReader())
    run_info.read()
    assert run_info.get_species() == "mouse"
