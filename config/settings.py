import streamlit as st
import os

def set_page():
    st.set_page_config(
        page_title="UIDAI Analytics Command Center",
        layout="wide",
        initial_sidebar_state="expanded"
    )

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
