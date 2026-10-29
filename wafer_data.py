"""MixedWM38 52x52 wafer map data quality validation."""
from pathlib import Path
import os
import numpy as np

CLASS_NAMES = ("Normal", "Center", "Donut", "Edge-Loc", "Edge-Ring",
               "Loc", "Near-Full", "Scratch", "Random")
VALID_DIE_VALUES = (0, 1, 2)

def resolve_data_path(path=None):
    return Path(path or os.getenv("WAFER_DATA_PATH") or
                Path(__file__).resolve().parent / "data" / "Wafer_Map_Datasets.npz").expanduser()

def label_to_class(row):
    arr = np.asarray(row)
    if arr.shape != (8,) or not np.isin(arr, (0, 1)).all() or arr.sum() > 1:
        raise ValueError("Expected eight binary labels with at most one active defect")
    return 0 if arr.sum() == 0 else int(np.argmax(arr)) + 1

def load_eligible(path=None, *, drop_invalid=True):
    """Isolate maps containing undocumented code 3; never silently relabel."""
    location = resolve_data_path(path)
    if not location.is_file():
        raise FileNotFoundError(f"Missing dataset: {location}; set WAFER_DATA_PATH")
    with np.load(location, allow_pickle=False) as source:
        maps, labels = source["arr_0"], source["arr_1"]
    if maps.ndim != 3 or maps.shape[1:] != (52, 52):
        raise ValueError(f"Expected maps (N,52,52), got {maps.shape}")
    if labels.shape != (len(maps), 8) or not np.isin(labels, (0, 1)).all():
        raise ValueError("Expected eight binary defect flags per wafer")
    singles = np.flatnonzero(labels.sum(axis=1) <= 1)
    invalid = ~np.isin(maps[singles], VALID_DIE_VALUES).all(axis=(1, 2))
    invalid_count = int(invalid.sum())
    if invalid_count and not drop_invalid:
        raise ValueError(f"{invalid_count} candidate maps have undocumented die values")
    selected = singles[~invalid] if drop_invalid else singles
    class_flags = labels[selected]
    y = np.where(class_flags.sum(axis=1) == 0, 0,
                 np.argmax(class_flags, axis=1) + 1).astype(np.int64)
    audit = {
        "raw_maps": int(len(maps)),
        "historical_normal_plus_single": int(len(singles)),
        "excluded_mixed_defect": int(len(maps)-len(singles)),
        "excluded_undocumented_die_value": invalid_count,
        "cleaned_usable": int(len(selected)),
        "class_counts": {n:int(np.sum(y==i)) for i,n in enumerate(CLASS_NAMES)},
        "invalid_policy": "exclude_complete_maps; never infer value 3",
    }
    return maps[selected], y, selected, audit

def die_counts(wafer):
    a=np.asarray(wafer)
    if a.shape!=(52,52) or not np.isin(a, VALID_DIE_VALUES).all():
        raise ValueError("Expected 52x52 wafer map with valid 0/1/2 states")
    passed=int(np.count_nonzero(a==1))
    failed=int(np.count_nonzero(a==2))
    active=passed+failed
    return {"pass_count":passed,"fail_count":failed,
            "fail_ratio": failed/active if active else 0.0}
