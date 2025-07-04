import streamlit as st
from data_utils import load_data, check_dataset_freshness
import pages.snapshot as snapshot
import pages.comparison as comparison
import pages.history as history

st.set_page_config(
    page_title="Chimpanzee Behavior Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    st.sidebar.title("Dashboard Settings")
    st.sidebar.write("Use the following options to customize the data visualization.")

    df = load_data()
    if df.empty:
        st.error("Data could not be loaded.")
        return
    check_dataset_freshness(df)

    query_type = st.sidebar.selectbox(
        "Select Query Type",
        ["Snapshot", "Comparison", "Behavior History"],
    )

    with st.sidebar.expander("About", expanded=False):
        st.markdown(
            "This dashboard visualizes chimpanzee behavioral data collected over time."
        )
        st.markdown("Dataset courtesy of the research team.")

    if query_type == "Snapshot":
        snapshot.run(df)
    elif query_type == "Comparison":
        comparison.run(df)
    elif query_type == "Behavior History":
        history.run(df)
    else:
        st.warning("Please select a query type.")


if __name__ == "__main__":
    main()
