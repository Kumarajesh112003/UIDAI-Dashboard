import streamlit as st
import plotly.express as px

def render(f_e, generate_uidai_plan):
    st.markdown("""
    <div class="methodology-box">
        <div class="methodology-header">METRIC DEFINITION: POPULATION AGING INDEX</div>
        <p><b>Formula:</b> <span class="highlight">Adult Enrollments (18+) / Child Enrollments (0-5)</span></p>
    </div>
    """, unsafe_allow_html=True)

    if f_e.empty:
        st.warning("No enrollment data")
        return

    age_cols = [c for c in f_e.columns if 'age' in c and 'total' not in c]
    if len(age_cols) < 2:
        st.warning("Age columns missing")
        return

    d_age = f_e.groupby(['state', 'district'])[age_cols].sum().reset_index()
    d_age['Aging_Index'] = d_age[age_cols[-1]] / (d_age[age_cols[0]] + 1)

    top = d_age.nlargest(10, 'Aging_Index')[['state', 'district', 'Aging_Index']]

    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.plotly_chart(
            px.bar(
                top, x='Aging_Index', y='district',
                orientation='h',
                title="Top Aging Districts",
                template='plotly_dark', height=500
            ),
            use_container_width=True
        )

    with c_right:
        st.dataframe(top, hide_index=True, use_container_width=True)
        run_ai = st.button("⚡ Generate AI Action Plan", key="ai_demo")

    if run_ai:
        with st.spinner("AI Analyst is reviewing demographics..."):
            ai = generate_uidai_plan("Demographic Aging", top.to_string())
            st.markdown(f"<div class='ai-box'><div class='ai-header'>AI STRATEGIC ADVISORY</div>{ai}</div>", unsafe_allow_html=True)
