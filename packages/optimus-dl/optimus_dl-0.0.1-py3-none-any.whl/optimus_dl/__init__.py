import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TORCHINDUCTOR_COMPILE_THREADS", "1")

import torch

from optimus_dl.core.bootstrap import bootstrap_module

torch.set_num_threads(1)
bootstrap_module(__name__)
