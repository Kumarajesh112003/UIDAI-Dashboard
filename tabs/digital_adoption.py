import streamlit as st
import plotly.express as px

def render(f_d, generate_uidai_plan):
    st.markdown("""
    <div class="methodology-box">
        <div class="methodology-header">DIGITAL SELF-SERVICE SCORE</div>
        <p>(Weekend Transactions / Total Transactions) × 100</p>
    </div>
    """, unsafe_allow_html=True)

    if f_d.empty or 'is_weekend' not in f_d.columns:
        st.warning("Digital indicators missing")
        return

    wk = f_d.groupby(['state', 'district', 'is_weekend'])['total_updates'].sum().unstack(fill_value=0)
    if 1 not in wk.columns:
        st.warning("Weekend data missing")
        return

    wk['Score'] = (wk[1] / (wk.sum(axis=1) + 1) * 100).round(2)
    low = wk.nsmallest(10, 'Score').reset_index()[['state', 'district', 'Score']]

    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.plotly_chart(
            px.bar(
                wk.nlargest(10, 'Score').reset_index(),
                x='Score', y='district',
                orientation='h',
                title="Digital Leaders",
                template='plotly_dark', height=500
            ),
            use_container_width=True
        )

    with c_right:
        st.dataframe(low, hide_index=True, use_container_width=True)
        run_ai = st.button("⚡ Generate AI Action Plan", key="ai_digital")

    if run_ai:
        with st.spinner("AI Analyst is reviewing digital trends..."):
            ai = generate_uidai_plan("Digital Literacy", low.to_string())
            st.markdown(f"<div class='ai-box'><div class='ai-header'>AI STRATEGIC ADVISORY</div>{ai}</div>", unsafe_allow_html=True)
