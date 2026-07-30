<div align="center">

# Formula 1 Race Prediction System

### End-to-end Formula 1 finishing-position prediction with historical data, circuit context, live-session adjustments, and Monte Carlo uncertainty

<p>
  <img src="https://img.shields.io/badge/Formula%201-Race%20Prediction-E10600?style=for-the-badge&logo=f1&logoColor=white" alt="Formula 1 Race Prediction">
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/scikit--learn-RandomForest-F7931E?style=flat-square&logo=scikitlearn&logoColor=white" alt="scikit-learn">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Next.js-Frontend-000000?style=flat-square&logo=nextdotjs&logoColor=white" alt="Next.js">
  <img src="https://img.shields.io/badge/React-Interactive%20Dashboard-20232A?style=flat-square&logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/Monte%20Carlo-Uncertainty-3acebc?style=flat-square&labelColor=0e6666" alt="Monte Carlo">
</p>

**Historical Form · Circuit Features · Driver and Team Priors · Prediction Intervals · Podium and Top-10 Probabilities**

</div>

---

<details>
<summary><strong>Quick navigation</strong></summary>

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [ML Model Specifications](#ml-model-specifications)
- [Circuit Features](#circuit-features)
- [Usage](#usage)
- [Notes](#notes)
- [Authors](#authors)

</details>

## Overview
This project is an end-to-end Formula 1 race prediction platform designed to predict finishing positions of drivers using historical race data, circuit characteristics, and advanced ML techniques. The system integrates data from multiple sources, includes Monte Carlo simulations for uncertainty, and provides a user-friendly Next.js frontend dashboard backed by a FastAPI backend.


---

## Features
- **Historical Race Data Integration:** Uses previous race results (2023–2025) to derive driver and team form.
- **Circuit-Specific Features:** Incorporates characteristics like track layout, long straights, street circuits, elevation, weather, and pit stop strategies.
- **Driver & Team Priors:** Pre-season and updated dynamic driver/team strengths including rookie and returnee status.
- **Live Session Adjustments:** Integrates FP1/FP2 session data when available for dynamic race predictions.
- **Machine Learning Model:** RandomForestRegressor with 1200 trees, OOB score, feature importance, and delta-target calculation (finish minus grid).
- **Uncertainty & Monte Carlo Simulation:** Provides prediction intervals (68% & 95%) and probability distributions for podium/top-10 finishes.
- **Backend & API:** FastAPI backend serving predictions, driver details, summary stats, and search functionality.
- **Frontend Dashboard:** Next.js app with React components, interactive tables, driver photos, circuit banners, and dynamic stats visualization.
- **Prediction Saving:** Automatic saving of trained models and feature matrices per race.


---

## Project Structure
```
F1_prediction_system/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app entrypoint
│   │   ├── model.py           # ML model pipeline and prediction logic
│   │   ├── features.py        # Feature engineering & driver/team forms
│   │   ├── config.py          # Circuit and season configuration
│   │   ├── schemas.py         # Pydantic schemas for API responses
│   │   ├── data/              # Stored predictions & feature files
│   │   └── f1cache/           # FastF1 cache
├── frontend/
│   ├── app/                   # Next.js 13 app directory
│   │   ├── page.tsx           # Homepage with predictions dashboard
│   │   ├── components/        # React components (tables, banners, driver cards)
│   │   ├── lib/api.ts         # API fetching helpers
│   │   └── styles/            # CSS / Tailwind configurations
├── notebooks/                 # Optional Jupyter notebooks for exploration
├── README.md                  # This file
└── requirements.txt           # Python backend dependencies
```


---

## Installation

### Backend
```bash
cd F1_prediction_system/backend
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd F1_prediction_system/frontend
npm install
npm run dev
# Access at http://localhost:3000
```


---

## ML Model Specifications
- **Algorithm:** RandomForestRegressor (sklearn)
- **Estimators:** 1200 trees
- **Max Depth:** None
- **Min Samples Leaf:** 16
- **Bootstrap:** True
- **OOB Score:** True
- **Target:** `finish_pos - grid_pos` (delta target)
- **Features:** Grid position, circuit priors, driver/team priors, historical form, blended 2026-adjusted strengths, weather, track layout, driver/team archetype forms.
- **Permutation & Tree-Based Feature Importance:** Available for top predictors.


---

## Circuit Features
Each circuit includes:
- `expected_stops`, `overtake_index`, `tow_importance`
- `is_low_df`, `is_street`, `long_straight_index`
- `braking_intensity`, `warmup_penalty`, `deg_rate`, `stint_len_typical`
- `surface_bumpiness`, `wind_sensitivity`, `track_limits_risk`, `elevation_change_index`
- `mechanical_failure_risk`, `corner_count`, `avg_speed_kph`
- `rain_prob_race`, `wet_lap_fraction`, `wet_start_prob`, `mixed_conditions_risk`

Circuit-specific parameters are stored in `config.py` and used in feature engineering.


---

## Usage
- **Run backend API:** `uvicorn app.main:app --reload`
- **Access predictions:** `/predictions/latest`, `/predictions/top10`, `/drivers/{driver_code}`
- **Frontend dashboard:** Visualizes predictions, probabilities, feature importance, and dynamic stats per race.
- **Update for next race:** Adjust `config.py` for new circuit features and update driver/team prior strengths.


---

## Notes
- Monte Carlo simulation allows probabilistic ranking and top-10/podium probabilities.
- Live session features improve accuracy but are optional (`--use_sessions`).
- Can train race-specific models by modifying `train_model` in `model.py`.
- Preprocessing ensures numerical consistency, imputation, and categorical encoding.


---

## Authors
Aryan Kumar - NIT Goa - Electronics & AI/ML enthusiast
