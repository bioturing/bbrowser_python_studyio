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