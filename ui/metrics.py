import streamlit as st

def show_metrics(f_e, f_d, f_b):
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("New Enrollments", int(f_e['total_enroll'].sum()))
    with c2:
        st.metric("Demographic Updates", int(f_d['total_updates'].sum()))
    with c3:
        st.metric("Biometric Updates", int(f_b['total_bio'].sum()))
    with c4:
        st.metric("Total Volume", int(
            f_e['total_enroll'].sum() + f_d['total_updates'].sum()
        ))
