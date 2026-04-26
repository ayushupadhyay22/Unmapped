# UNMAPPED

A skill mapping engine for local jobs, designed to bridge the gap between informal skills and formal economic opportunities in the age of AI.

## Project Overview
UNMAPPED is an infrastructure layer (protocol) that connects a young person's real skills to real economic opportunity. It translates informal, uncredentialed experience into standardized, portable skill profiles and evaluates displacement risk against automation exposure.

## Modules

### Module 01: Skills Signal Engine
**Explanation:** This module takes informal, uncredentialed experience (e.g., "I fix phones and sell airtime at the market") and translates it into a standardized, machine-readable skill profile using official taxonomies like ESCO or O*NET.
**How to Test:**
1. Open the Streamlit Dashboard (`http://localhost:8501`).
2. Type an informal skill description into the text area.
3. Select your "Country Context" and "Economy Type" from the sidebar.
4. Click **"Analyze Skills & Assess Risk"**.
5. The API will process the text and return standardized skills under the **"Recognized Skills"** section.

### Module 02: AI Readiness & Displacement Risk Lens
**Explanation:** Once skills are standardized, this module cross-references them against automation datasets (like the Frey & Osborne scores). It calculates the displacement risk for those specific skills in the selected country/context and recommends adjacent, durable skills to learn.
**How to Test:**
1. Submit an informal skill description via the Streamlit Dashboard.
2. Look at the right side of the results panel.
3. The **"Displacement Risk"** gauge will show the likelihood of automation (based on dataset lookups).
4. Check the **"Recommended Adjacent Skills"** under the left panel for upskilling suggestions based on the risk profile.

## Code Structure

```text
├── backend/
│   ├── database.py       # SQLAlchemy engine and SQLite connection
│   ├── main.py           # FastAPI application and core logic endpoints
│   └── models.py         # SQLAlchemy ORM models
├── data/                 # Raw CSV/Excel datasets and SQLite database
├── frontend/
│   └── app.py            # Streamlit dashboard UI
├── scripts/
│   └── process_data.py   # Data ingestion script
├── run.sh                # Startup script for both servers
└── requirements.txt      # Python dependencies
```

The UNMAPPED application is divided into a robust backend architecture and a lightweight frontend visualization layer. Below is a breakdown of how the codebase works.

### 1. Database Initialization (`scripts/process_data.py`)
This script uses **Pandas** and **SQLAlchemy** to construct a local SQLite database (`data/unmapped.db`). 
- It ingests official ISCO-08 taxonomies and multiple global/LMIC automation risk datasets (e.g., Frey & Osborne, Wittgenstein Education Projections).
- Run this script to populate the database tables with all the realistic skill and automation data required for the application to function.

### 2. Backend API (`backend/main.py` & `backend/database.py`)
The backend is built with **FastAPI**, creating an open protocol that any government or NGO portal could consume.
- **`database.py` & `models.py`**: Configures the SQLAlchemy database engine and defines the ORM models (`EscoSkill`, `AutomationRisk`) used to query the data cleanly.
- **`analyze-skills` Endpoint**: This is the core logic engine. It expects a JSON payload containing the user's informal experience, country, and economic context.
    - **Step 1 (Mapping):** It attempts to map the informal text to standard ESCO skills. It checks for an `OPENAI_API_KEY`. If present, it uses a **Retrieval-Augmented Generation (RAG-lite)** approach, sending the text and a list of valid database skills to an LLM for intelligent selection.
    - **Fallback:** If the API key is missing or fails, it gracefully falls back to a local **Fuzzy String Matching** algorithm (`difflib`) to ensure the demo never crashes during a presentation.
    - **Step 2 (Risk Query):** Once the standardized skills are identified (e.g., "Electronics Mechanic"), the backend queries the `automation_risk` table in SQLite for the specific combination of skill + country + context.
    - It then averages the risk scores and collects unique "adjacent skills" to return a final JSON profile.

### 3. Frontend Dashboard (`frontend/app.py`)
The frontend is built purely in Python using **Streamlit**. It requires zero HTML/CSS/JS.
- It provides a sidebar for configuring the "Country-Agnostic" parameters.
- It takes the user's text input, formats it, and POSTs it directly to the FastAPI backend.
- Upon receiving the JSON response, it dynamically renders metrics, progress bars (for displacement risk), and lists of suggested skills. It also explicitly displays the mapping method (LLM vs Fallback) used by the backend.

### 4. Runner Script (`run.sh`)
A Bash utility that installs requirements, executes the database initialization script, and concurrently boots both the FastAPI server on port `8000` and the Streamlit dashboard on port `8501`.

## Datasets Included
The UNMAPPED engine leverages several robust datasets to map skills and assess automation risk globally, covering **40 countries across 6 regions** (Sub-Saharan Africa, South Asia, Southeast Asia, MENA, Latin America & Caribbean, and Central Asia).

### Core Datasets & Sources
1. **ISCO-08 Taxonomy**: The official International Standard Classification of Occupations, providing a standard global framework for mapping informal skills.
2. **Frey & Osborne Automation Risk**: The foundational study (Frey & Osborne, 2017) on computerization probabilities for various occupations.
3. **Demographic & Education Projections**: Wittgenstein Center (WIC) Population and Human Capital Projections forecasting skill gaps and educational trajectories across different age cohorts (specifically the 15–29 youth labour force).
4. **LMIC Calibration & Sector Data**: Uses indicators like internet penetration (ITU), informal economy share (ILO), and average wages (World Bank) to calculate real-world automation arrival.

### File Inventory
| File | Rows | Coverage | Use |
|------|------|----------|-----|
| `frey_osborne_isco.csv` | 332 | Global occupations | Base automation scores |
| `frey_osborne_lmic.csv` | 1,992 | 332 × 6 regions | LMIC-calibrated scores |
| `lmic_automation_calibration_full.csv` | 40 | 40 countries | Discount factors + infra |
| `wittgenstein_education_projections_full.csv` | 160 | 40 countries × 4 years | Education trajectories |
| `lmic_sector_automation_risk_full.csv` | 400 | 40 × 10 sectors | Sector-level risk |
| `wic_automation_combined_full.csv` | 160 | 40 countries × 4 years | Education + automation merged |

### Country Coverage (40 countries, 6 regions)
- **Sub-Saharan Africa (16)**: Ghana, Nigeria, Senegal, Côte d'Ivoire, Mali, Guinea, Kenya, Uganda, Tanzania, Ethiopia, Rwanda, Mozambique, Zambia, South Africa, Zimbabwe, Malawi
- **South Asia (6)**: India, Bangladesh, Pakistan, Nepal, Sri Lanka, Myanmar
- **Southeast Asia (7)**: Malaysia, Indonesia, Philippines, Vietnam, Thailand, Cambodia, Laos
- **MENA (4)**: Morocco, Egypt, Tunisia, Jordan
- **Latin America & Caribbean (5)**: Colombia, Peru, Bolivia, Honduras, Haiti
- **Central Asia (2)**: Uzbekistan, Kyrgyzstan

### LMIC Calibration Methodology
A raw probability score of 0.97 for a retail cashier isn't realistic in an environment lacking infrastructure. We apply a `fo_discount_factor` derived from three structural factors specific to Low- and Middle-Income Countries (LMICs):
1. **Wage vs Automation Cost Parity**: When average monthly wages are significantly lower than the cost of deploying automation, employers lack the economic incentive to automate.
2. **Infrastructure Constraints**: Low internet penetration and unreliable electricity limit which automation technologies can actually be deployed.
3. **Informal Economy Share**: Informal markets operate largely outside formal automation adoption channels, shielding many roles from immediate technological displacement.
## Tech Stack
* **Backend:** FastAPI (Python)
* **Frontend:** Streamlit (Python)
* **Database:** SQLite & Pandas 
* **AI/NLP:** LLM API (OpenAI) with pure-Python Fuzzy Fallback.

## Getting Started

### 1. Environment Variables
To enable the LLM-powered skill mapping and AI risk analysis, you must set your OpenAI API key as an environment variable. 
Create a `.env` file in the root directory and add the following line:
```env
OPENAI_API_KEY="your-api-key-here"
```
Alternatively, you can export it directly in your terminal:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize the Database
Before running the application, you need to ingest the latest taxonomy and risk datasets into SQLite:
```bash
python scripts/process_data.py
```

### 4. Run the Application
You can run the full stack simultaneously using the provided bash script:
```bash
chmod +x run.sh
./run.sh
```

- **API Docs (Swagger):** `http://localhost:8000/docs`
- **Frontend Dashboard:** `http://localhost:8501`
- **To Stop:** Press `Ctrl+C` in the terminal to kill both servers.

### 5. Testing the Core Logic Locally
If you want to quickly test the skill-mapping and task-distance recommendation logic without spinning up the frontend UI, you can use the included test script. Open `test_script.py`, modify the inputs (like `description` and `region`), and run it directly in your terminal:
```bash
python test_script.py
```
This script bypasses the API port and tests the core backend Python functions directly against the database, printing out the `automation_risk_score` and `adjacent_skills_suggested` response!

### Troubleshooting
If you encounter an `Address already in use` error when running `./run.sh`, it means a previous instance of the server is still running in the background. You can forcefully kill these processes using the following commands:

To kill the backend (port 8000):
```bash
lsof -ti:8000 | xargs kill -9
```

To kill the frontend (port 8501):
```bash
lsof -ti:8501 | xargs kill -9
```
