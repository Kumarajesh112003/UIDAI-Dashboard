import streamlit as st
import plotly.express as px

def render(f_b, generate_uidai_plan):
    st.markdown("""
    <div class="methodology-box">
        <div class="methodology-header">SERVICE LOAD & DESERTS</div>
        <p>Total biometric updates per district</p>
    </div>
    """, unsafe_allow_html=True)

    if f_b.empty:
        st.warning("No biometric data")
        return

    serv = f_b.groupby(['state', 'district'])['total_bio'].sum().reset_index()
    low = serv.nsmallest(10, 'total_bio')

    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.plotly_chart(
            px.treemap(
                serv, path=['state', 'district'],
                values='total_bio',
                title="Service Volume Heatmap",
                template='plotly_dark', height=500
            ),
            use_container_width=True
        )

    with c_right:
        st.dataframe(low, hide_index=True, use_container_width=True)
        run_ai = st.button("⚡ Generate AI Action Plan", key="ai_service")

    if run_ai:
        with st.spinner("AI Analyst is identifying service gaps..."):
            ai = generate_uidai_plan("Service Delivery Gaps", low.to_string())
            st.markdown(f"<div class='ai-box'><div class='ai-header'>AI STRATEGIC ADVISORY</div>{ai}</div>", unsafe_allow_html=True)
