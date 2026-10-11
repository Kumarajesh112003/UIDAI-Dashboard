import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from groq import Groq
import glob
import os
import zipfile
import re

# ==========================================
# API CONFIGURATION (loaded from .env locally, or host secrets in deployment)
# ==========================================
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
try:
    if not GROQ_API_KEY:
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    pass
# ==========================================

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="UIDAI Analytics Command Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UNZIP DATASETS (Run once on startup) ---
def unzip_data(zip_name, extract_to):
    if os.path.exists(zip_name):
        with zipfile.ZipFile(zip_name, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        # print(f"Extracted {zip_name}") # Commented out for cleaner logs

os.makedirs('./data_enrolment', exist_ok=True)
os.makedirs('./data_demographic', exist_ok=True)
os.makedirs('./data_biometric', exist_ok=True)

# Ensure these zip files are uploaded to your Hugging Face Files tab!
unzip_data('api_data_aadhar_enrolment.zip', './data_enrolment')
unzip_data('api_data_aadhar_demographic.zip', './data_demographic')
unzip_data('api_data_aadhar_biometric.zip', './data_biometric')

# --- ENTERPRISE DARK THEME CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E6E6E6; font-family: 'Segoe UI', sans-serif; }
    section[data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    [data-testid="stSidebar"] label { font-size: 12px !important; color: #8B949E !important; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] { font-size: 13px !important; min-height: 35px; }
    h1 { color: #58A6FF !important; font-weight: 700; letter-spacing: -0.5px; font-size: 2.2rem; }
    h2 { color: #C9D1D9 !important; font-size: 1.6rem; border-bottom: 1px solid #30363D; padding-bottom: 10px; margin-top: 30px; }
    h3 { color: #8B949E !important; font-size: 1.2rem; font-weight: 500; }
    .metric-card { background: linear-gradient(145deg, #1F242C, #161B22); border: 1px solid #30363D; border-radius: 8px; padding: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .metric-value { font-size: 28px; font-weight: 700; color: #58A6FF; margin: 5px 0; }
    .metric-label { font-size: 11px; color: #8B949E; text-transform: uppercase; letter-spacing: 1px; }
    .methodology-box { background-color: rgba(56, 139, 253, 0.1); border-left: 4px solid #1F6FEB; padding: 20px; border-radius: 4px; margin-bottom: 25px; color: #C9D1D9; font-size: 14px; line-height: 1.6; }
    .methodology-header { color: #58A6FF; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; font-size: 13px; }
    .ai-box { background-color: #0D1117; border: 1px solid #A371F7; border-radius: 8px; padding: 20px; margin-top: 25px; box-shadow: 0 0 15px rgba(163, 113, 247, 0.1); }
    .ai-header { color: #A371F7; font-weight: 700; font-size: 1.1rem; margin-bottom: 15px; border-bottom: 1px solid #A371F7; padding-bottom: 10px; display: flex; align-items: center; gap: 10px; }
    .action-box { background-color: rgba(46, 160, 67, 0.1); border: 1px solid rgba(46, 160, 67, 0.4); border-radius: 8px; padding: 25px; margin-top: 30px; }
    .action-title { color: #3FB950; font-weight: 700; font-size: 16px; margin-bottom: 15px; border-bottom: 1px solid rgba(46, 160, 67, 0.4); padding-bottom: 8px; }
    .stButton button { background: linear-gradient(90deg, #7C3AED, #5B21B6); color: white; border: none; font-weight: 600; width: 100%; }
    .spacer { height: 25px; }
    .highlight { color: #A5D6FF; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# --- AI ENGINE ---
def generate_uidai_plan(topic, data_summary):
    if not GROQ_API_KEY or "gsk_" not in GROQ_API_KEY:
        return "⚠️ AI Configuration Error: Invalid API Key."
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
        Role: Senior Strategic Consultant for UIDAI.
        Topic: {topic}
        Data Context: {data_summary}
        Task: Provide a 3-point strategic action plan.
        Format:
        1. Strategic Diagnosis: (1 sentence on what the data implies)
        2. Operational Response: (Specific action to tackle the problem)
        3. Policy Recommendation: (Long-term fix)
        Tone: Government Executive, Brief. Max 150 words.
        """
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5, max_tokens=1500, top_p=1, stream=False, stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI Connection Error: {str(e)}"

# --- ADVANCED DATA CLEANING ---
def clean_state_names(df):
    # 1. Clean State Names
    if 'state' in df.columns:
        df['state'] = df['state'].astype(str).str.strip().str.title()
        
        # Remove rows containing Digits (0-9) OR Question Marks (?)
        df = df[~df['state'].str.contains(r'[\d?]', regex=True)].copy()
        
        # Fix Standard Spells
        replacements = {
            "Andaman & Nicobar Islands": "Andaman And Nicobar Islands", 
            "Dadra & Nagar Haveli": "Dadra And Nagar Haveli",
            "Daman & Diu": "Daman And Diu", 
            "W. Bengal": "West Bengal", 
            "West  Bengal": "West Bengal"
        }
        df['state'] = df['state'].replace(replacements)
        
        # Remove garbage/short abbreviations
        df = df[df['state'].str.len() > 3]

    # 2. Clean District Names (Added logic to remove '?')
    if 'district' in df.columns:
        df['district'] = df['district'].astype(str).str.strip().str.title()
        
        # Remove rows where District contains Digits OR '?'
        df = df[~df['district'].str.contains(r'[\d?]', regex=True)].copy()
        
        # Remove empty or extremely short district names (garbage)
        df = df[df['district'].str.len() > 2]

    return df

@st.cache_data
def load_data():
    def load_folder(path):
        files = glob.glob(os.path.join(path, "**/*.csv"), recursive=True)
        dfs = []
        for f in files:
            try: dfs.append(pd.read_csv(f))
            except: pass
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    df_e, df_d, df_b = load_folder("./data_enrolment"), load_folder("./data_demographic"), load_folder("./data_biometric")
    
    for df in [df_e, df_d, df_b]:
        if not df.empty:
            df.columns = df.columns.str.lower().str.strip()
            if 'date' in df.columns: df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
            cols = df.select_dtypes(include=np.number).columns
            df[cols] = df[cols].fillna(0)
            
            # Apply Improved Cleaning
            df = clean_state_names(df)
            
    return df_e, df_d, df_b

def engineer_features(df_e, df_d, df_b):
    if not df_e.empty:
        age_cols = [c for c in df_e.columns if 'age' in c]
        df_e['total_enroll'] = df_e[age_cols].sum(axis=1)
    if not df_d.empty:
        demo_cols = [c for c in df_d.columns if 'demo' in c or 'age' in c]
        df_d['total_updates'] = df_d[demo_cols].sum(axis=1)
        if 'date' in df_d.columns: df_d['is_weekend'] = df_d['date'].dt.dayofweek.isin([5, 6]).astype(int)
    if not df_b.empty:
        bio_cols = [c for c in df_b.columns if 'bio' in c or 'age' in c]
        df_b['total_bio'] = df_b[bio_cols].sum(axis=1)
    return df_e, df_d, df_b

with st.spinner('System Boot: Loading & Cleaning Data...'):
    raw_e, raw_d, raw_b = load_data()
    df_e, df_d, df_b = engineer_features(raw_e, raw_d, raw_b)

# --- SIDEBAR ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png", width=160)
st.sidebar.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
st.sidebar.header("FILTER DASHBOARD")

if not df_e.empty:
    # Safe Filter for Dropdown
    states = sorted([s for s in df_e['state'].dropna().unique().tolist() 
                    if str(s) != "10000" and str(s) != "Daman And Diu" and str(s) != "Jammu And Kashmir" and str(s) != "West Bengal" and str(s) != "West Bangal" and str(s) != "Dadra And Nagar Haveli" and str(s) != "Dadra And Nagar Haveli And Daman And Diu" and str(s) != "Westbengal" and str(s) != "Andaman And Nicobar Islands" and not str(s).isdigit()])
                     
    sel_state = st.sidebar.selectbox("SELECT STATE", ["All"] + states)
    st.sidebar.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
    
    if sel_state != "All":
        districts = sorted([d for d in df_e[df_e['state'] == sel_state]['district'].unique().tolist() 
                            if str(d) != "10000" and not str(d).isdigit()])
        sel_dist = st.sidebar.selectbox("SELECT DISTRICT", ["All"] + districts)
    else: 
        sel_dist = "All"
else: 
    sel_state, sel_dist = "All", "All"

st.sidebar.markdown("---")
st.sidebar.markdown("""<div style='color: #8B949E; font-size: 11px;'><b>SYSTEM STATUS</b><br><span style='color:#3FB950'>● Online</span><br>AI Module: Active</div>""", unsafe_allow_html=True)

def filter_data(df):
    if df.empty: return df
    temp = df.copy()
    if sel_state != "All": temp = temp[temp['state'] == sel_state]
    if sel_dist != "All": temp = temp[temp['district'] == sel_dist]
    return temp

f_e, f_d, f_b = filter_data(df_e), filter_data(df_d), filter_data(df_b)

# --- MAIN LAYOUT ---
st.title("UIDAI ANALYTICS COMMAND CENTER")
st.markdown(f"**DATA SCOPE:** {sel_state.upper()} > {sel_dist.upper()}")
st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

if f_e.empty and f_d.empty:
    st.error("No data found. Please check uploaded files.")
    st.stop()

# --- KPI METRICS ---
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>New Enrollments</div><div class='metric-value'>{f_e['total_enroll'].sum():,.0f}</div></div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='metric-card'><div class='metric-label'>Demographic Updates</div><div class='metric-value'>{f_d['total_updates'].sum():,.0f}</div></div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='metric-card'><div class='metric-label'>Biometric Updates</div><div class='metric-value'>{f_b['total_bio'].sum():,.0f}</div></div>", unsafe_allow_html=True)
with c4: st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Volume</div><div class='metric-value'>{(f_e['total_enroll'].sum() + f_d['total_updates'].sum()):,.0f}</div></div>", unsafe_allow_html=True)

st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

# --- TABS SECTION ---
tabs = st.tabs(["MIGRATION", "DEMOGRAPHICS", "SERVICE DELIVERY", "DIGITAL ADOPTION", "CHILD WELFARE", "ANOMALIES"])

# === TAB 1: MIGRATION ===
with tabs[0]:
    st.markdown("""
    <div class="methodology-box">
        <div class="methodology-header">METRIC DEFINITION: MIGRATION INTENSITY SCORE</div>
        <p><b>Meaning:</b> Identifies districts where population growth is driven by incoming migration (labor influx) rather than local birth rates.</p>
        <p><b>Formula:</b> <span class="highlight">Total Demographic Updates / (New Enrollments + 1)</span></p>
        <p><b>Strategic Thresholds:</b><br>
        • <span style='color:#58A6FF'>Score > 2.0</span>: <b>High In-Migration</b> (Industrial Hubs/Cities)<br>
        • <span style='color:#A371F7'>Score 0.5 - 2.0</span>: <b>Balanced Growth</b><br>
        • <span style='color:#58A6FF'>Score < 0.5</span>: <b>Natural Growth</b> (Source Villages)</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not f_e.empty and not f_d.empty and 'district' in f_e.columns:
        m_e = f_e.groupby(['state', 'district'])['total_enroll'].sum().reset_index()
        m_d = f_d.groupby(['state', 'district'])['total_updates'].sum().reset_index()
        mig = pd.merge(m_e, m_d, on=['state', 'district'], how='outer').fillna(0)
        mig['Score'] = mig['total_updates'] / (mig['total_enroll'] + 1)
        mig['Type'] = pd.cut(mig['Score'], bins=[0, 0.5, 2.0, float('inf')], labels=['Natural Growth', 'Balanced', 'In-Migration'])
        
        # --- FLIPPED LAYOUT [2:1] ---
        c_left, c_right = st.columns([2, 1])
        
        # Left: Main Visualization
        with c_left:
            st.plotly_chart(px.scatter(mig, x='total_enroll', y='total_updates', size='Score', color='Type', 
                             hover_name='district', hover_data=['state'], title="Migration Matrix", 
                             color_discrete_map={'Natural Growth': '#3FB950', 'Balanced': '#D29922', 'In-Migration': '#F85149'}, 
                             template='plotly_dark', height=500), width='stretch')

        # Right: Data & Actions
        with c_right:
            st.subheader("Top Migration Hubs")
            top = mig.nlargest(10, 'Score')[['state', 'district', 'Score']]
            st.dataframe(top, hide_index=True, width='stretch')
            st.markdown("---")
            run_ai = st.button("⚡ Generate AI Action Plan", key="ai_mig")

        # Full Width AI
        if run_ai:
            with st.spinner("AI Analyst is reviewing migration data..."):
                ai_response = generate_uidai_plan("Migration Patterns", top.to_string())
                st.markdown(f"""<div class='ai-box'><div class='ai-header'>AI STRATEGIC ADVISORY</div>{ai_response}</div>""", unsafe_allow_html=True)

# === TAB 2: DEMOGRAPHICS ===
with tabs[1]:
    st.markdown("""
    <div class="methodology-box">
        <div class="methodology-header">METRIC DEFINITION: POPULATION AGING INDEX</div>
        <p><b>Meaning:</b> Analyzes the generational structure of the district's applicant pool to target age-specific infrastructure.</p>
        <p><b>Formula:</b> <span class="highlight">Adult Enrollments (18+) / Child Enrollments (0-5)</span></p>
        <p><b>Strategic Thresholds:</b><br>
        • <span style='color:#58A6FF'>Score > 3.0</span>: <b>Aging Population</b> (Needs Healthcare/Pension Services)<br>
        • <span style='color:#A371F7'>Score < 1.5</span>: <b>Youth Bulge</b> (Needs Schools/Child Welfare)</p>
    </div>
    """, unsafe_allow_html=True)

    if not f_e.empty:
        age_cols = [c for c in f_e.columns if 'age' in c and 'total' not in c]
        if 'district' in f_e.columns and len(age_cols) >= 2:
            d_age = f_e.groupby(['state', 'district'])[age_cols].sum().reset_index()
            d_age['Aging_Index'] = d_age[age_cols[-1]] / (d_age[age_cols[0]] + 1)
            top = d_age.nlargest(10, 'Aging_Index')[['state', 'district', 'Aging_Index']]
            
            c_left, c_right = st.columns([2, 1])
            
            # Left: Chart
            with c_left: 
                st.plotly_chart(px.bar(top, x='Aging_Index', y='district', orientation='h', title="Top Aging Districts", template='plotly_dark', height=500), width='stretch')

            # Right: Table
            with c_right:
                st.subheader("High Aging Districts") 
                st.dataframe(top, hide_index=True, width='stretch')
                st.markdown("---")
                run_ai = st.button("⚡ Generate AI Action Plan", key="ai_demo")

            if run_ai:
                with st.spinner("AI Analyst is reviewing demographics..."):
                    ai_response = generate_uidai_plan("Demographic Aging", top.to_string())
                    st.markdown(f"""<div class='ai-box'><div class='ai-header'>🤖 AI STRATEGIC ADVISORY</div>{ai_response}</div>""", unsafe_allow_html=True)

# === TAB 3: SERVICE DELIVERY ===
with tabs[2]:
    st.markdown("""
    <div class="methodology-box">
        <div class="methodology-header">METRIC DEFINITION: SERVICE LOAD & DESERTS</div>
        <p><b>Meaning:</b> Maps the operational load across districts to identify areas with critical infrastructure gaps or overcrowding.</p>
        <p><b>Formula:</b> <span class="highlight">Total Sum of Biometric Updates per District</span></p>
        <p><b>Strategic Thresholds:</b><br>
        • <b>High Volume</b>: Potential Overcrowding (Requires Queue Management)<br>
        • <b>Bottom 10% Volume</b>: Service Deserts (Requires Mobile Vans/New Centers)</p>
    </div>
    """, unsafe_allow_html=True)

    if not f_b.empty and 'district' in f_b.columns:
        serv = f_b.groupby(['state', 'district'])['total_bio'].sum().reset_index()
        top_low = serv.nsmallest(10, 'total_bio')[['state', 'district', 'total_bio']]
        
        c_left, c_right = st.columns([2, 1])
        
        # Left: Chart
        with c_left: 
            st.plotly_chart(px.treemap(serv, path=['state', 'district'], values='total_bio', title="Service Volume Heatmap", template='plotly_dark', height=500), width='stretch')

        # Right: Table
        with c_right:
            st.subheader("Critical Service Gaps")
            st.dataframe(top_low, hide_index=True, width='stretch')
            st.markdown("---")
            run_ai = st.button("⚡ Generate AI Action Plan", key="ai_serv")

        if run_ai:
            with st.spinner("AI Analyst is identifying service gaps..."):
                ai_response = generate_uidai_plan("Service Delivery Gaps", top_low.to_string())
                st.markdown(f"""<div class='ai-box'><div class='ai-header'>🤖 AI STRATEGIC ADVISORY</div>{ai_response}</div>""", unsafe_allow_html=True)

# === TAB 4: DIGITAL ADOPTION ===
with tabs[3]:
    st.markdown("""
    <div class="methodology-box">
        <div class="methodology-header">METRIC DEFINITION: DIGITAL SELF-SERVICE SCORE</div>
        <p><b>Meaning:</b> Uses weekend activity as a proxy for tech-savvy populations who prefer online self-service portals over visiting centers.</p>
        <p><b>Formula:</b> <span class="highlight">(Weekend Transactions / Total Transactions) * 100</span></p>
        <p><b>Strategic Thresholds:</b><br>
        • <span style='color:#3FB950'>Score > 40%</span>: <b>High Digital Literacy</b><br>
        • <span style='color:#F85149'>Score < 20%</span>: <b>Low Literacy</b> (Requires Digital Awareness Camps)</p>
    </div>
    """, unsafe_allow_html=True)

    if not f_d.empty and 'is_weekend' in f_d.columns:
        d_wk = f_d.groupby(['state', 'district', 'is_weekend'])['total_updates'].sum().unstack(fill_value=0)
        if 1 in d_wk.columns:
            d_wk['Score'] = (d_wk[1] / (d_wk[0] + d_wk[1] + 1) * 100).round(2)
            low = d_wk.nsmallest(10, 'Score').reset_index()[['state', 'district', 'Score']]
            
            c_left, c_right = st.columns([2, 1])
            
            # Left: Chart
            with c_left: 
                st.plotly_chart(px.bar(d_wk.nlargest(10, 'Score').reset_index(), x='Score', y='district', orientation='h', title="Digital Leaders", template='plotly_dark', height=500), width='stretch')

            # Right: Table
            with c_right:
                st.subheader("Low Digital Adoption")
                st.dataframe(low, hide_index=True, width='stretch')
                st.markdown("---")
                run_ai = st.button("⚡ Generate AI Action Plan", key="ai_dig")

            if run_ai:
                with st.spinner("AI Analyst is reviewing digital trends..."):
                    ai_response = generate_uidai_plan("Digital Literacy", low.to_string())
                    st.markdown(f"""<div class='ai-box'><div class='ai-header'>🤖 AI STRATEGIC ADVISORY</div>{ai_response}</div>""", unsafe_allow_html=True)

# === TAB 5: CHILD WELFARE ===
with tabs[4]:
    st.markdown("""
    <div class="methodology-box">
        <div class="methodology-header">METRIC DEFINITION: CHILD RETENTION RATE</div>
        <p><b>Meaning:</b> Tracks the percentage of children enrolled at birth (0-5) who return for mandatory biometric updates (5-17).</p>
        <p><b>Formula:</b> <span class="highlight">(Biometric Updates 5-17 / Infant Enrollments 0-5) * 100</span></p>
        <p><b>Strategic Thresholds:</b><br>
        • <span style='color:#3FB950'>Rate > 80%</span>: <b>Good Retention</b><br>
        • <span style='color:#F85149'>Rate < 50%</span>: <b>Critical Attrition</b> (Risk of 'Missing Children')</p>
    </div>
    """, unsafe_allow_html=True)

    if not f_e.empty and not f_b.empty:
        e_col = next((c for c in f_e.columns if '0' in c and '5' in c), None)
        b_col = next((c for c in f_b.columns if '5' in c and '17' in c), None)
        if e_col and b_col:
            c_en = f_e.groupby(['state', 'district'])[e_col].sum().reset_index()
            c_bi = f_b.groupby(['state', 'district'])[b_col].sum().reset_index()
            merged = pd.merge(c_en, c_bi, on=['state', 'district'])
            merged.columns = ['State', 'District', 'Enrolled', 'Retained']
            merged['Rate'] = (merged['Retained'] / (merged['Enrolled'] + 1) * 100).round(1)
            critical = merged.nsmallest(10, 'Rate')[['State', 'District', 'Rate']]
            
            c_left, c_right = st.columns([2, 1])
            
            # Left: Chart
            with c_left:
                fig = go.Figure(go.Funnel(y = ["Infant Cohort", "Biometric Cohort"], x = [merged['Enrolled'].sum(), merged['Retained'].sum()], textinfo = "value+percent initial"))
                fig.update_layout(title="Aggregate Retention Funnel", template='plotly_dark', height=500)
                st.plotly_chart(fig, width='stretch')

            # Right: Table
            with c_right:
                st.subheader("Critical Zones")
                st.dataframe(critical, hide_index=True, width='stretch')
                st.markdown("---")
                run_ai = st.button("⚡ Generate AI Action Plan", key="ai_child")

            if run_ai:
                with st.spinner("AI Analyst is reviewing child welfare data..."):
                    ai_response = generate_uidai_plan("Child Retention & Welfare", critical.to_string())
                    st.markdown(f"""<div class='ai-box'><div class='ai-header'>🤖 AI STRATEGIC ADVISORY</div>{ai_response}</div>""", unsafe_allow_html=True)

# === TAB 6: ANOMALIES ===
with tabs[5]:
    st.markdown("""
    <div class="methodology-box">
        <div class="methodology-header">METHOD: ISOLATION FOREST AI</div>
        <p><b>Meaning:</b> Unsupervised Machine Learning algorithm that detects statistical outliers in daily transaction volumes.</p>
        <p><b>Logic:</b> Items that are few and different are easier to 'isolate'. Anomalies have shorter path lengths in the random forest trees.</p>
        <p><b>Application:</b><br>
        • <b>Sudden Spikes:</b> Potential Bulk Fraud or Unscheduled Camps<br>
        • <b>Sudden Drops:</b> System Failure or Operator Strike</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Run Operational Anomaly Scan"):
        if not f_d.empty and 'date' in f_d.columns:
            ts = f_d.groupby('date')['total_updates'].sum().reset_index()
            if len(ts) > 10:
                scaler = StandardScaler()
                X = scaler.fit_transform(ts[['total_updates']])
                model = IsolationForest(contamination=0.05, random_state=42)
                ts['anomaly'] = model.fit_predict(X)
                anoms = ts[ts['anomaly'] == -1]
                
                c_left, c_right = st.columns([2, 1])
                
                # Left: Chart
                with c_left: 
                    st.plotly_chart(px.scatter(ts, x='date', y='total_updates', color=ts['anomaly'].astype(str), title="Volume Time Series", template='plotly_dark', height=500), width='stretch')

                # Right: Table
                with c_right:
                    st.subheader("Flagged Anomalies")
                    if not anoms.empty:
                        st.dataframe(anoms.head(10), hide_index=True, width='stretch')
                        st.markdown("---")
                        run_ai = st.button("⚡ Analyze Anomalies with AI", key="ai_anom")
                    else: 
                        st.success("Operations stable.")
                        run_ai = False
                
                if run_ai and not anoms.empty:
                    with st.spinner("AI is investigating anomalies..."):
                        ai_response = generate_uidai_plan("Operational Anomalies", anoms.to_string())
                        st.markdown(f"""<div class='ai-box'><div class='ai-header'>🤖 AI STRATEGIC ADVISORY</div>{ai_response}</div>""", unsafe_allow_html=True)
