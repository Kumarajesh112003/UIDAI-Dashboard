import streamlit as st
import pandas as pd
import plotly.express as px

def render(f_e, f_d, generate_uidai_plan):
    st.markdown("""
    <div class="methodology-box">
        <div class="methodology-header">METRIC DEFINITION: MIGRATION INTENSITY SCORE</div>
        <p><b>Meaning:</b> Identifies districts where population growth is driven by incoming migration.</p>
        <p><b>Formula:</b> <span class="highlight">Total Demographic Updates / (New Enrollments + 1)</span></p>
    </div>
    """, unsafe_allow_html=True)

    if f_e.empty or f_d.empty:
        st.warning("Insufficient data")
        return

    m_e = f_e.groupby(['state', 'district'])['total_enroll'].sum().reset_index()
    m_d = f_d.groupby(['state', 'district'])['total_updates'].sum().reset_index()

    mig = pd.merge(m_e, m_d, on=['state', 'district'], how='outer').fillna(0)
    mig['Score'] = mig['total_updates'] / (mig['total_enroll'] + 1)
    mig['Type'] = pd.cut(
        mig['Score'],
        bins=[0, 0.5, 2.0, float('inf')],
        labels=['Natural Growth', 'Balanced', 'In-Migration']
    )

    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.plotly_chart(
            px.scatter(
                mig, x='total_enroll', y='total_updates',
                size='Score', color='Type',
                hover_name='district', hover_data=['state'],
                title="Migration Matrix",
                color_discrete_map={
                    'Natural Growth': '#3FB950',
                    'Balanced': '#D29922',
                    'In-Migration': '#F85149'
                },
                template='plotly_dark', height=500
            ),
            use_container_width=True
        )

    with c_right:
        st.subheader("Top Migration Hubs")
        top = mig.nlargest(10, 'Score')[['state', 'district', 'Score']]
        st.dataframe(top, hide_index=True, use_container_width=True)
        run_ai = st.button("⚡ Generate AI Action Plan", key="ai_migration")

    if run_ai:
        with st.spinner("AI Analyst is reviewing migration data..."):
            ai = generate_uidai_plan("Migration Patterns", top.to_string())
            st.markdown(f"<div class='ai-box'><div class='ai-header'>AI STRATEGIC ADVISORY</div>{ai}</div>", unsafe_allow_html=True)
