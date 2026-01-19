import streamlit as st
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def render(f_d, generate_uidai_plan):
    st.markdown("""
    <div class="methodology-box">
        <div class="methodology-header">ISOLATION FOREST ANOMALY DETECTION</div>
        <p>Detects abnormal spikes or drops in transaction volume</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.button("Run Operational Anomaly Scan"):
        return

    if f_d.empty or 'date' not in f_d.columns:
        st.warning("Date-based data missing")
        return

    ts = f_d.groupby('date')['total_updates'].sum().reset_index()
    if len(ts) < 10:
        st.warning("Insufficient time series")
        return

    X = StandardScaler().fit_transform(ts[['total_updates']])
    model = IsolationForest(contamination=0.05, random_state=42)
    ts['anomaly'] = model.fit_predict(X)
    anoms = ts[ts['anomaly'] == -1]

    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.plotly_chart(
            px.scatter(
                ts, x='date', y='total_updates',
                color=ts['anomaly'].astype(str),
                title="Transaction Time Series",
                template='plotly_dark', height=500
            ),
            use_container_width=True
        )

    with c_right:
        if anoms.empty:
            st.success("Operations stable.")
            return

        st.dataframe(anoms.head(10), hide_index=True, use_container_width=True)
        run_ai = st.button("⚡ Analyze Anomalies with AI", key="ai_anom")

    if run_ai:
        with st.spinner("AI is investigating anomalies..."):
            ai = generate_uidai_plan("Operational Anomalies", anoms.to_string())
            st.markdown(f"<div class='ai-box'><div class='ai-header'>AI STRATEGIC ADVISORY</div>{ai}</div>", unsafe_allow_html=True)
