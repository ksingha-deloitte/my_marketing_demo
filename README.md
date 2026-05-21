# Agentic Campaign Optimization Engine

A Streamlit workshop app demonstrating an AI agent analyzing marketing campaign data, detecting underperformers, rewriting ad creative, and reallocating budget.

## Project Structure

- `app.py` - Main Streamlit application.
- `data/data_generation.py` - Dummy marketing data generation and Excel export.
- `data/marketing_data.xlsx` - Generated dataset exported by the app.

## How to Run

1. Create a Python environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Features

- Campaign dashboard with interactive Plotly charts
- Automatic anomaly detection for low CTR / high CPA segments
- Simulated AI creative optimization for underperforming audiences
- Budget reallocation engine with projected conversion uplift
