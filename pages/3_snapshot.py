import streamlit as st
from data_utils import load_data, check_dataset_freshness
from logic import filter_data, calculate_deviations, get_behavior_color_map
from ui import (
    select_period,
    select_filters,
    create_bar_chart,
    create_deviation_bar_chart,
    download_filtered_data,
)

st.set_page_config(
    page_title="Snapshot",
    layout="wide",
    initial_sidebar_state="expanded",
)

def run(df):
    """Render the snapshot page."""
    start_date, end_date = select_period(df)
    filter_option, selected_animal, selected_sex, selected_groups = select_filters(df)

    df_filtered = filter_data(
        df,
        start_date,
        end_date,
        filter_option,
        animal=selected_animal,
        sexes=selected_sex,
        groups=selected_groups,
    )

    if filter_option == "By Individual" and selected_animal:
        chart_title = f"Behavior Dashboard for {selected_animal}"
    elif filter_option == "By Sex and Social Group":
        sex_text = ", ".join(selected_sex) if selected_sex else "All Sexes"
        group_text = ", ".join(selected_groups) if selected_groups else "All Social Groups"
        chart_title = f"Behavior Dashboard by Sex: {sex_text} | Social Groups: {group_text}"
    else:
        chart_title = "Behavior Dashboard"

    if not df_filtered.empty:
        st.title(chart_title)
        color_map = get_behavior_color_map(df)
        df_sorted = df_filtered.sort_values(by="Percentage", ascending=False)
        create_bar_chart(
            df_sorted,
            behavior_order=df_sorted["Unified Behavior"].tolist(),
            color_map=color_map,
            title="Activity Budget Distribution",
            y_max=df_sorted["Percentage"].max(),
        )
        download_filtered_data(df_sorted, key_prefix="filtered_")

        if filter_option == "By Individual" and selected_animal:
            deviations = calculate_deviations(df, df_filtered, selected_animal)
            create_deviation_bar_chart(deviations, "Behavior Deviations")
            st.subheader("Deviation Summary")
            st.dataframe(deviations[["Percentage", "Individual", "Group", "All"]])
    else:
        st.warning("No data available for the selected filters.")


df = load_data()
if not df.empty:
    check_dataset_freshness(df)
    run(df)
else:
    st.error("Data could not be loaded.")
