import pandas as pd
import streamlit as st

@st.cache_data
def load_data(path="reports/behavior.csv"):
    """Load the behavior dataset.

    Parameters
    ----------
    path : str
        CSV path to read.

    Returns
    -------
    pd.DataFrame
    """
    try:
        df = pd.read_csv(path)
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    except FileNotFoundError:
        st.warning("The file 'behavior.csv' was not found. Upload one below.")
        uploaded = st.file_uploader("Upload behavior.csv", type="csv")
        if uploaded is not None:
            try:
                df = pd.read_csv(uploaded)
                df["Date"] = pd.to_datetime(df["Date"])
                return df
            except Exception as exc:
                st.error(f"Failed to read uploaded file: {exc}")
    except Exception as exc:
        st.error(f"Failed to load data: {exc}")
    return pd.DataFrame()


def check_dataset_freshness(df, days=90):
    """Warn if the dataset has not been updated recently."""
    if df.empty:
        return
    latest_date = df["Date"].max()
    if (pd.Timestamp.now() - latest_date) > pd.Timedelta(days=days):
        st.info(
            "Behavior data might be outdated. Consider uploading a newer CSV file."
        )
