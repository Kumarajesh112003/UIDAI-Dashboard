import streamlit as st

def render_sidebar(df_e):
    st.sidebar.header("FILTER DASHBOARD")

    if df_e.empty:
        return "All", "All"

    states = sorted(df_e['state'].dropna().unique())
    sel_state = st.sidebar.selectbox("SELECT STATE", ["All"] + states)

    if sel_state != "All":
        districts = sorted(df_e[df_e['state'] == sel_state]['district'].unique())
        sel_dist = st.sidebar.selectbox("SELECT DISTRICT", ["All"] + districts)
    else:
        sel_dist = "All"

    return sel_state, sel_dist
