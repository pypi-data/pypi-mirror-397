# Linear 我们之前改过代码，类名是 Linear
from .linear import Linear

# RMSNorm 我们没动过代码，类名还是 PlyRMSNorm，所以这里用别名 (as)
from .rmsnorm import PlyRMSNorm as RMSNorm

__version__ = "1.0.5"
