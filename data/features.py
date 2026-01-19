def engineer_features(df_e, df_d, df_b):
    if not df_e.empty:
        age_cols = [c for c in df_e.columns if 'age' in c]
        df_e['total_enroll'] = df_e[age_cols].sum(axis=1)

    if not df_d.empty:
        demo_cols = [c for c in df_d.columns if 'demo' in c or 'age' in c]
        df_d['total_updates'] = df_d[demo_cols].sum(axis=1)
        if 'date' in df_d.columns:
            df_d['is_weekend'] = df_d['date'].dt.dayofweek.isin([5, 6]).astype(int)

    if not df_b.empty:
        bio_cols = [c for c in df_b.columns if 'bio' in c or 'age' in c]
        df_b['total_bio'] = df_b[bio_cols].sum(axis=1)

    return df_e, df_d, df_b
