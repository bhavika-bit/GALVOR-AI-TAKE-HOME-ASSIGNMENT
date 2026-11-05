import re
import numpy as np
import pandas as pd


def txt(value):
    if value is None or value is pd.NA:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def handle(value):
    value = txt(value).strip().lower()
    value = re.sub(r"^https?://(www\.)?instagram\.com/", "", value)
    value = value.strip("/@ ").split("/")[0]
    return value


def col(df, names):
    if df is None or df.empty and len(df.columns) == 0:
        return None
    lookup = {str(c).strip().lower(): c for c in df.columns}
    return next((lookup[str(n).strip().lower()] for n in names if str(n).strip().lower() in lookup), None)


def numeric(series):
    return pd.to_numeric(series, errors="coerce")


def score(value):
    try:
        return float(np.clip(float(value), 0, 100))
    except (TypeError, ValueError):
        return 0.0


def split_list(value):
    return [x.strip() for x in txt(value).split(";") if x.strip()]
