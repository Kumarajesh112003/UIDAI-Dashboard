import pandas as pd
import numpy as np
import glob
import os
import streamlit as st
from data.cleaning import clean_state_names

@st.cache_data
def load_data():
    def load_folder(path):
        files = glob.glob(os.path.join(path, "**/*.csv"), recursive=True)
        dfs = []
        for f in files:
            try:
                dfs.append(pd.read_csv(f))
            except:
                pass
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    df_e = load_folder("./data_enrolment")
    df_d = load_folder("./data_demographic")
    df_b = load_folder("./data_biometric")

    for df in [df_e, df_d, df_b]:
        if not df.empty:
            df.columns = df.columns.str.lower().str.strip()
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
            num_cols = df.select_dtypes(include=np.number).columns
            df[num_cols] = df[num_cols].fillna(0)
            df[:] = clean_state_names(df)

    return df_e, df_d, df_b
