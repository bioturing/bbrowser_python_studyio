import h5py
import os
class Expression:
    def __init__(self, h5path):
        self.path = h5path
    
    def exists(self) -> bool:
        return os.path.isfile(self.path)

    def features(self):
        with h5py.File(self.path, "r") as fopen:
            ft = fopen["bioturing/features"][:]
        return ft
    
    # TODO: needs more APIs