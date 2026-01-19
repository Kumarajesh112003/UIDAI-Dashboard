import re

def clean_state_names(df):
    if 'state' in df.columns:
        df['state'] = df['state'].astype(str).str.strip().str.title()
        df = df[~df['state'].str.contains(r'[\d?]', regex=True)]

        replacements = {
            "Andaman & Nicobar Islands": "Andaman And Nicobar Islands",
            "Dadra & Nagar Haveli": "Dadra And Nagar Haveli",
            "Daman & Diu": "Daman And Diu",
            "W. Bengal": "West Bengal",
            "West  Bengal": "West Bengal"
        }
        df['state'] = df['state'].replace(replacements)
        df = df[df['state'].str.len() > 3]

    if 'district' in df.columns:
        df['district'] = df['district'].astype(str).str.strip().str.title()
        df = df[~df['district'].str.contains(r'[\d?]', regex=True)]
        df = df[df['district'].str.len() > 2]

    return df
