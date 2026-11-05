import json
from pathlib import Path
import pandas as pd

EXPECTED = {
    "ads": {"ad_id", "launch_date", "transcript", "hook_line", "spend_inr", "impressions", "purchases", "revenue_inr"},
    "creators": {"creator_id", "handle", "followers", "persona", "voice", "themes", "what_feels_native"},
    "posts": {"creator_id", "handle", "post_url", "posted_on", "plays", "likes", "comments", "reshares", "caption"},
    "audience": {"creator_id", "handle", "women_pct", "men_pct", "age_split", "top_cities", "top_countries"},
}


def load_config(path="config.json"):
    path = Path(path).resolve()
    config = json.loads(path.read_text(encoding="utf-8"))
    config["_project_root"] = str(path.parent)
    return config


def load_datasets(config):
    root = Path(config.get("_project_root", Path.cwd()))
    frames, missing = {}, []
    for name, raw_path in config["data_paths"].items():
        p = Path(raw_path)
        if not p.is_absolute():
            p = root / p
        if not p.exists():
            frames[name] = pd.DataFrame()
            missing.append(f"{name}: {p}")
            continue
        try:
            frames[name] = pd.read_csv(p, low_memory=False)
        except UnicodeDecodeError:
            frames[name] = pd.read_csv(p, encoding="utf-8-sig", low_memory=False)
    return frames, missing


def validate_datasets(frames):
    issues = []
    for name, required in EXPECTED.items():
        df = frames.get(name, pd.DataFrame())
        if df.empty:
            issues.append(f"{name}: file is empty or could not be loaded")
            continue
        absent = sorted(required - set(df.columns))
        if absent:
            issues.append(f"{name}: missing expected columns: {', '.join(absent)}")
    creators = frames.get("creators", pd.DataFrame())
    posts = frames.get("posts", pd.DataFrame())
    if not creators.empty and "handle" in creators and creators["handle"].duplicated().any():
        issues.append("creators: duplicate handles detected")
    if not creators.empty and not posts.empty and {"handle"}.issubset(creators.columns) and {"handle"}.issubset(posts.columns):
        known = set(creators["handle"].dropna().astype(str).str.lower().str.lstrip("@"))
        orphan = set(posts["handle"].dropna().astype(str).str.lower().str.lstrip("@")) - known
        if orphan:
            issues.append(f"posts: {len(orphan)} handles do not match creators.csv")
    return issues


def data_health(frames):
    report = {}
    for name, df in frames.items():
        report[name] = {
            "rows": int(len(df)), "columns": int(len(df.columns)),
            "duplicate_rows": int(df.duplicated().sum()) if not df.empty else 0,
            "missing_cells": int(df.isna().sum().sum()) if not df.empty else 0,
        }
    return report
