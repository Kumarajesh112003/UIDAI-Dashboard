# UIDAI Dashboard

The **UIDAI Dashboard** is a data analytics and AI-based web application that helps understand population trends and service usage using UIDAI-related data.  
It converts raw enrollment, demographic update, and biometric activity data into **clear insights and visual reports** that support better planning and decision-making.
---

##  Project Purpose

Population patterns in India change due to migration, aging, urban growth, and digital adoption.  
Although UIDAI systems collect large amounts of data, useful insights are not always easy to see.

This project aims to:
- Analyze UIDAI operational data
- Highlight important trends and gaps
- Detect unusual activity early
- Support data-driven governance and inclusion

---

##  Key Objectives

- Study enrollment and demographic update trends
- Identify migration-heavy districts
- Analyze population aging patterns
- Measure digital service usage
- Detect operational anomalies using AI
- Generate AI-based recommendations

---

##  Main Features

###  Data Analysis
- Migration Intensity Score
- Population Aging Index
- Child Retention Analysis
- Service Load and Coverage Gaps
- Digital Adoption Score

###  AI Insights
- Automatic AI-generated action plans
- Clear explanations for critical districts
- Policy-support recommendations

###  Interactive Dashboard
- Charts, tables, and visual summaries
- District and state-level views
- Easy-to-use Streamlit interface

###  Anomaly Detection
- Machine learning–based detection
- Finds unusual spikes or drops in activity
- Helps in early risk identification

---

##  Project Structure

UIDAI-Dashboard/
│
├                   
├── config/
│   ├── settings.py            
│   ├── secrets_example.py     
│
├── data/
│   ├── unzip.py                
│   ├── loader.py              
│   ├── cleaning.py         
│   ├── features.py           
│
├── ai/
│   └── advisor.py              
│
├── ui/
│   ├── theme.py              
│   ├── sidebar.py           
│   ├── metrics.py           
│
├── tabs/
│   ├── migration.py
│   ├── demographics.py
│   ├── service_delivery.py
│   ├── digital_adoption.py
│   ├── child_welfare.py
│   └── anomalies.py
│
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE


##  Important Metrics (Simple Explanation)

| Metric | Meaning |
|------|--------|
| Migration Intensity | Shows districts with high migration |
| Aging Index | Compares adult and child enrollments |
| Digital Adoption Score | Shows use of online services |
| Child Retention Rate | Tracks biometric continuity of children |
| Anomaly Detection | Finds unusual activity patterns |

---

##  Technologies Used

- **Frontend:** Streamlit
- **Charts:** Plotly
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** Scikit-learn
- **AI Advisory:** LLM-based analysis
- **Deployment:** Hugging Face Spaces

---

##  Deployment

The project is deployed and accessible online:

🔗 **Live Dashboard:**  
https://the-rock1-uidai-dashboard.hf.space

You can explore the dashboard without installing anything.

---
