# Ultralytics YOLO 🚀, AGPL-3.0 license

__version__ = "8.3.100"

import os

# Set ENV variables (place before imports)
if not os.environ.get("OMP_NUM_THREADS"):
    os.environ["OMP_NUM_THREADS"] = "1"  # default for reduced CPU utilization during training

from visaionlibrary.utils.yoloe.models import YOLO, YOLOE
from visaionlibrary.utils.yoloe.utils import ASSETS, SETTINGS
from visaionlibrary.utils.yoloe.utils.checks import check_yolo as checks
from visaionlibrary.utils.yoloe.utils.downloads import download

settings = SETTINGS
__all__ = (
    "__version__",
    "ASSETS",
    "YOLO",
    "YOLOE",
    "checks",
    "download",
    "settings",
)
