# Chimpanzee Behavior Dashboard

This project provides a Streamlit dashboard to explore chimpanzee behavior data stored in `reports/behavior.csv`.

## Running locally

1. Install Python 3.11 or later.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the dashboard:
   ```bash
   streamlit run app.py
   ```
4. The app uses a dark theme defined in `.streamlit/config.toml`.

## Updating data

Place an updated `behavior.csv` inside the `reports/` directory. You can also upload a new CSV from the dashboard when prompted if the file is missing.

## Exporting results

The dashboard allows downloading filtered data as CSV or Excel files via the sidebar.

## Behavior history

Use the sidebar to choose between **Snapshot**, **Comparison** and **Behavior History** pages. Snapshot shows a summary for a given period, Comparison lets you place several panels side by side and Behavior History displays how an individual's behavior changes over time.
