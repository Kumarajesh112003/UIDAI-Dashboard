<div align="center">

# 🛡️ UIDAI Analytics Command Center

**Turn raw Aadhaar enrolment and update data into clear insights, district by district.**

[![Live Demo](https://img.shields.io/badge/Live_Demo-Open_Dashboard-brightgreen?style=for-the-badge)](https://uidai-dashboard-03.streamlit.app)

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Charts-3F4F75?logo=plotly&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-Anomaly_Detection-F7931E?logo=scikitlearn&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-AI_Advisor-8A2BE2)

### 🔗 [**https://uidai-dashboard-03.streamlit.app**](https://uidai-dashboard-03.streamlit.app)

</div>

---

## 📌 What is this?

India's population keeps shifting because of migration, ageing, urban growth and the move to digital services. UIDAI systems collect a huge amount of data about this, but the useful patterns are hard to see in raw tables.

This dashboard reads **enrolment, demographic-update and biometric-update records** and turns them into simple charts, scores and AI-written action plans that help with planning and decision-making.

---

## ✨ Features

| Tab | What it shows | Key question it answers |
|---|---|---|
| 🚚 **Migration** | Migration Intensity Score per district | Which districts are gaining people from elsewhere? |
| 👴 **Demographics** | Population Aging Index | Where do we need pension and healthcare, or schools? |
| 🏢 **Service Delivery** | Biometric update volume per district | Which districts are overcrowded, and which are underserved? |
| 📱 **Digital Adoption** | Weekend activity as a digital proxy | Where do people use self-service the most or the least? |
| 👶 **Child Welfare** | Child Retention Rate | How many children return for their mandatory biometric update? |
| 🚨 **Anomalies** | Isolation Forest outlier scan | Are there unusual spikes or drops in daily activity? |

Every tab also has a **⚡ Generate AI Action Plan** button. It sends that tab's findings to an LLM and returns a short, three-point plan: diagnosis, operational response and policy recommendation.

You can filter the whole dashboard by **state** and **district** from the sidebar.

---

## 📐 How the scores work

| Metric | Formula | Reading it |
|---|---|---|
| **Migration Intensity** | Demographic updates ÷ (New enrolments + 1) | Above 2.0 means high in-migration, below 0.5 means natural growth |
| **Aging Index** | Adult enrolments (18+) ÷ Child enrolments (0-5) | Above 3.0 means an ageing population, below 1.5 means a youth bulge |
| **Digital Adoption** | Weekend updates ÷ Total updates × 100 | Above 40% is high, below 20% is low |
| **Child Retention** | Biometric updates (5-17) ÷ Infant enrolments (0-5) × 100 | Above 80% is good, below 50% is critical |
| **Anomaly Detection** | Isolation Forest on daily update totals | Flags the most unusual 5% of days |

---

## 🧰 Tech stack

- **Dashboard:** Streamlit
- **Charts:** Plotly
- **Data:** Pandas, NumPy, Parquet (PyArrow)
- **Machine learning:** scikit-learn (Isolation Forest)
- **AI advisor:** Groq API (`openai/gpt-oss-20b`)
- **Hosting:** Streamlit Community Cloud

---

## ⚡ How the data is handled

The raw files hold about **5 million rows**, one per pincode per day. The dashboard only ever needs totals per **date, state and district**, so the rows are merged once, ahead of time:

```
raw zips  ──►  data/build_aggregates.py  ──►  data_agg/*.parquet  ──►  dashboard
(~5M rows)        (run once)                    (~230K rows, <1 MB)
```

The charts come out identical, and the app starts in about two seconds using a fraction of the memory.

---

## 🚀 Run it on your computer

```bash
# 1. Get the code
git clone https://github.com/Kumarajesh112003/UIDAI-Dashboard.git
cd UIDAI-Dashboard

# 2. Install the packages
pip install -r requirements.txt

# 3. Add your Groq API key (free at https://console.groq.com/keys)
cp .env.example .env
#    then open .env and replace your_api_key_here with your key

# 4. Start the app
streamlit run app.py
```

It opens at http://localhost:8501.

**Updating the data:** put the three raw zip files in the project folder and run `python data/build_aggregates.py` to rebuild `data_agg/`.

> 🔒 The API key lives in `.env`, which is git-ignored. On Streamlit Cloud, set it under **Settings → Secrets** as `GROQ_API_KEY = "your_key"`. Never commit a real key.

---

## 📁 Project structure

```
UIDAI-Dashboard/
├── app.py                     # The dashboard (run this)
├── data_agg/                  # Pre-aggregated data used by the app
│   ├── enrolment.parquet
│   ├── demographic.parquet
│   └── biometric.parquet
├── data/
│   └── build_aggregates.py    # Builds data_agg/ from the raw zips
├── api_data_aadhar_*.zip      # Raw source data (used only to rebuild data_agg/)
├── requirements.txt           # Python packages
├── .env.example               # Template for your API key
├── LICENSE
└── README.md
```

The `ai/`, `config/`, `tabs/`, `ui/` and the other `data/` modules are an earlier split-up version of the same logic. The running app doesn't import them.

---

## 📄 License

Released under the terms in the [LICENSE](LICENSE) file.
