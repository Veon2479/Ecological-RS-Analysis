### https://nbviewer.org/github/pytroll/pytroll-examples/blob/main/satpy/satpy_rayleigh_iband_enhanced.ipynb
### https://satpy.readthedocs.io/en/stable/install.html
### $ conda create -c conda-forge -n satpy_env python satpy

from pyparsing import null_debug_action
from satpy.scene import Scene
from satpy import find_files_and_readers
from glob import glob
from pathlib import Path

import config

### AreaDefinition ### AreaDefinition ### AreaDefinition
### AreaDefinition ### AreaDefinition ### AreaDefinition
### AreaDefinition ### AreaDefinition ### AreaDefinition
# https://github.com/pytroll/satpy/blob/main/satpy/etc/areas.yaml
