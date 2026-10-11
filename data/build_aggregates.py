"""Build small per-(date, state, district) files from the raw pincode-level zips.

Run once from the project root after the raw data changes:
    python data/build_aggregates.py

The dashboard only ever sums values per state/district/date, so merging the
pincode rows first gives identical charts with ~99% fewer rows.
"""
import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data_agg"

SOURCES = {
    "enrolment": "api_data_aadhar_enrolment.zip",
    "demographic": "api_data_aadhar_demographic.zip",
    "biometric": "api_data_aadhar_biometric.zip",
}


def read_zip(zip_path):
    frames = []
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if name.lower().endswith(".csv"):
                with zf.open(name) as f:
                    frames.append(pd.read_csv(io.BytesIO(f.read())))
    return pd.concat(frames, ignore_index=True)


def aggregate(df):
    # Same preparation the app applies to the raw rows
    df.columns = df.columns.str.lower().str.strip()
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    num_cols = df.select_dtypes(include=np.number).columns
    df[num_cols] = df[num_cols].fillna(0)
    df["state"] = df["state"].astype(str).str.strip().str.title()

    # pincode is not used anywhere in the dashboard
    value_cols = [c for c in num_cols if c != "pincode"]
    return (
        df.groupby(["date", "state", "district"], dropna=False)[value_cols]
        .sum()
        .reset_index()
    )


if __name__ == "__main__":
    OUT_DIR.mkdir(exist_ok=True)
    for name, zip_name in SOURCES.items():
        raw = read_zip(ROOT / zip_name)
        agg = aggregate(raw)
        agg.to_parquet(OUT_DIR / f"{name}.parquet", index=False)
        print(f"{name}: {len(raw):,} rows -> {len(agg):,} rows")
