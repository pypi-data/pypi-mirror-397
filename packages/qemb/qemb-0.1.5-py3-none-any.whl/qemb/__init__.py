
from . import cut_cluster
from . import jobs
from . import find_dirs
from . import write_inputs
from . import tackle_poscar
from importlib.metadata import version, PackageNotFoundError

# Version is managed by setuptools_scm

try:
    __version__ = version("qemb")
except PackageNotFoundError:
    # 如果包没有安装（比如在源码目录直接运行），尝试读取 setuptools_scm 生成的文件
    try:
        from ._version import version as __version__
    except ImportError:
        __version__ = "unknown"


__all__ = [
    "cut_cluster",
    "find_dirs", 
    "jobs",
    "tackle_poscar",
    "write_inputs",
    "__version__",
]

