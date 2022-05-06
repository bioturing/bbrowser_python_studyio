from typing import Union
try:
    from typing import Literal
except:
    from typing_extensions import Literal

NUM = Union[int, float]

SPECIES_LIST = Literal["human", "mouse", "rat", "zebrafish", "fly",
                        "m_fascicularis", "other"]
OMICS_LIST = Literal["RNA", "ADT", "PRTB", "spatial"]
UNIT_TYPE_LIST = Literal["norm", "raw"]
UNIT_TRANSFORM_LIST = Literal["none", "log2"]
UNIT_LIST = Literal["umi", "lognorm", "read", "cpm", "tpm", "rpkm", "fpkm",
                    "unknown"]
INPUT_FORMAT_LIST = Literal["fullmatrix", "mtx", "h5matrix",
                            "crisprfullmatrix", "visium", "h5visium", "bcs",
                            "seurat", "scanpy", "loomamgen", "fastq",
                            "csv", "txt", "tsv", "nanostring"] # No UPPER CASE allowed for backward compatibility purpose
NORMALIZATION_LIST = Literal["none", "lognorm"]

METADATA_TYPE_LIST = Literal["category", "numeric"]
UNASSIGNED = "Unassigned"
METADATA_TYPE_NUMERIC = "numeric"
METADATA_TYPE_CATEGORICAL = "category"
BIOTURING_UNASSIGNED = "Unassigned"