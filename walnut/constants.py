from typing import Literal, Union

NUM = Union[int, float]

SPECIES_LIST = Literal["human", "mouse", "rat", "zebrafish", "fly",
                        "m_fascicularis", "other"]
OMICS_LIST = Literal["RNA", "ADT", "PRTB", "spatial"]
UNIT_TYPE_LIST = Literal["norm", "raw"]
UNIT_TRANSFORM_LIST = Literal["none", "log2"]
UNIT_LIST = Literal["umi", "lognorm", "read", "cpm", "tpm", "rpkm", "fpkm",
                    "unknown"]
INPUT_FORMAT_LIST = Literal["fullMatrix", "mtx", "h5matrix",
                            "crisprFullMatrix", "visium", "h5visium", "bcs",
                            "seurat", "scanpy", "loomAmgen", "fastq"]
NORMALIZATION_LIST = Literal["none", "lognorm"]