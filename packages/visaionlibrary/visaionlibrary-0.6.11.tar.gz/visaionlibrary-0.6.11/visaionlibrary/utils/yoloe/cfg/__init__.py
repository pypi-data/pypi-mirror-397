# Ultralytics YOLO 🚀, AGPL-3.0 license
# Simplified version - only prediction functionality

from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Union

from visaionlibrary.utils.yoloe.utils import (
    DEFAULT_CFG_DICT,
    RANK,
    RUNS_DIR,
    TESTS_RUNNING,
    IterableSimpleNamespace,
    yaml_load,
)

# Simplified keys for prediction only
CFG_FLOAT_KEYS = {"batch"}
CFG_FRACTION_KEYS = {"conf", "iou"}
CFG_INT_KEYS = {"max_det", "vid_stride", "line_width"}
CFG_BOOL_KEYS = {
    "save", "exist_ok", "verbose", "half", "dnn", "show",
    "save_txt", "save_conf", "save_crop", "save_frames",
    "show_labels", "show_conf", "visualize", "augment",
    "agnostic_nms", "retina_masks", "show_boxes",
}


def cfg2dict(cfg):
    """Converts a configuration object to a dictionary."""
    if isinstance(cfg, (str, Path)):
        cfg = yaml_load(cfg)
    elif isinstance(cfg, SimpleNamespace):
        cfg = vars(cfg)
    return cfg


def get_cfg(cfg: Union[str, Path, Dict, SimpleNamespace] = DEFAULT_CFG_DICT, overrides: Dict = None):
    """Load and merge configuration data from a file or dictionary, with optional overrides."""
    cfg = cfg2dict(cfg)

    # Merge overrides
    if overrides:
        overrides = cfg2dict(overrides)
        if "save_dir" not in cfg:
            overrides.pop("save_dir", None)
        cfg = {**cfg, **overrides}

    # Special handling for numeric project/name
    for k in "project", "name":
        if k in cfg and isinstance(cfg[k], (int, float)):
            cfg[k] = str(cfg[k])
    if cfg.get("name") == "model":
        cfg["name"] = cfg.get("model", "").split(".")[0]
        # LOGGER.warning(f"WARNING ⚠️ 'name=model' automatically updated to 'name={cfg['name']}'.")

    # Type checks (simplified)
    check_cfg(cfg)

    return IterableSimpleNamespace(**cfg)


def check_cfg(cfg, hard=False):
    """Checks configuration argument types and values (simplified version)."""
    for k, v in cfg.items():
        if v is not None:
            if k in CFG_FLOAT_KEYS and not isinstance(v, (int, float)):
                cfg[k] = float(v)
            elif k in CFG_FRACTION_KEYS:
                if not isinstance(v, (int, float)):
                    cfg[k] = v = float(v)
                # if not (0.0 <= v <= 1.0):
                #     LOGGER.warning(f"WARNING ⚠️ '{k}={v}' is out of range [0.0, 1.0]")
            elif k in CFG_INT_KEYS and not isinstance(v, int):
                cfg[k] = int(v)
            elif k in CFG_BOOL_KEYS and not isinstance(v, bool):
                cfg[k] = bool(v)


def get_save_dir(args, name=None):
    """Returns the directory path for saving outputs."""
    if getattr(args, "save_dir", None):
        save_dir = args.save_dir
    else:
        from visaionlibrary.utils.yoloe.utils.files import increment_path
        from visaionlibrary.utils.yoloe.utils import ROOT

        project = args.project or (ROOT.parent / "tests/tmp/runs" if TESTS_RUNNING else RUNS_DIR) / args.task
        name = name or args.name or f"{args.mode}"
        save_dir = increment_path(Path(project) / name, exist_ok=args.exist_ok if RANK in {-1, 0} else True)

    return Path(save_dir)
