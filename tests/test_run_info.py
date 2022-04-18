from walnut.readers import TextReader
import tempfile
import os
import json

def test_run_info_0():
    from walnut.run_info import RunInfo
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