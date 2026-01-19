import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render(f_e, f_b, generate_uidai_plan):
    st.markdown("""
    <div class="methodology-box">
        <div class="methodology-header">CHILD RETENTION RATE</div>
        <p>(Biometric Updates 5–17 / Infant Enrollments 0–5) × 100</p>
    </div>
    """, unsafe_allow_html=True)

    e_col = next((c for c in f_e.columns if '0' in c and '5' in c), None)
    b_col = next((c for c in f_b.columns if '5' in c and '17' in c), None)

    if not e_col or not b_col:
        st.warning("Required age cohorts missing")
        return

    e = f_e.groupby(['state', 'district'])[e_col].sum().reset_index()
    b = f_b.groupby(['state', 'district'])[b_col].sum().reset_index()

    m = pd.merge(e, b, on=['state', 'district'])
    m['Rate'] = (m[b_col] / (m[e_col] + 1) * 100).round(1)
    critical = m.nsmallest(10, 'Rate')

    c_left, c_right = st.columns([2, 1])

    with c_left:
        fig = go.Figure(go.Funnel(
            y=["Infant Cohort", "Biometric Cohort"],
            x=[m[e_col].sum(), m[b_col].sum()],
            textinfo="value+percent initial"
        ))
        fig.update_layout(template='plotly_dark', height=500)
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        st.dataframe(critical[['state', 'district', 'Rate']], hide_index=True, use_container_width=True)
        run_ai = st.button("⚡ Generate AI Action Plan", key="ai_child")

    if run_ai:
        with st.spinner("AI Analyst is reviewing child welfare data..."):
            ai = generate_uidai_plan("Child Retention & Welfare", critical.to_string())
            st.markdown(f"<div class='ai-box'><div class='ai-header'>AI STRATEGIC ADVISORY</div>{ai}</div>", unsafe_allow_html=True)
