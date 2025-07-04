import pandas as pd
import streamlit as st
from data_utils import load_data, check_dataset_freshness
from logic import filter_data, get_behavior_color_map
from ui import (
    select_period,
    select_filters,
    create_bar_chart,
    download_filtered_data,
)

st.set_page_config(
    page_title="🌑 Comparison",
    layout="wide",
    initial_sidebar_state="expanded",
)


def run(df):
    """Render the comparison page."""
    num_fields = st.sidebar.selectbox("Number of Comparison Fields", [2, 3, 4], index=0)
    st.title("Behavior Comparison Dashboard")

    columns = st.columns(num_fields)
    max_y = 0
    comparison_data = []
    chart_titles = []

    for i in range(num_fields):
        with columns[i]:
            key_prefix = f"field_{i}_"
            start_date, end_date = select_period(df, key_prefix=key_prefix)
            filter_option, selected_animal, selected_sex, selected_groups = select_filters(df, key_prefix=key_prefix)

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
                chart_title = f"{selected_animal} | {start_date.strftime('%B %Y')} - {end_date.strftime('%B %Y')}"
            elif filter_option == "By Sex and Social Group":
                sex_text = ", ".join(selected_sex) if selected_sex else "All Sexes"
                group_text = ", ".join(selected_groups) if selected_groups else "All Social Groups"
                date_text = (
                    f"{start_date.strftime('%B %Y')} - {end_date.strftime('%B %Y')}"
                    if start_date != end_date
                    else start_date.strftime("%B %Y")
                )
                chart_title = f"Sex: {sex_text} | Groups: {group_text} | Dates: {date_text}"
            else:
                chart_title = "Behavior Comparison"

            chart_titles.append(chart_title)
            st.subheader(chart_title)

            if not df_filtered.empty:
                df_grouped = (
                    df_filtered.groupby("Unified Behavior", observed=False)["Percentage"].mean().reset_index()
                )
                current_max = df_grouped["Percentage"].max()
                max_y = max(max_y, current_max)
                comparison_data.append((df_filtered, chart_title))
            else:
                comparison_data.append((pd.DataFrame(), chart_title))

    behavior_order = None
    color_map = get_behavior_color_map(df)

    for i in range(num_fields):
        df_filtered, chart_title = comparison_data[i]
        with columns[i]:
            if not df_filtered.empty:
                if i == 0:
                    df_grouped_first = (
                        df_filtered.groupby("Unified Behavior", observed=False)["Percentage"].mean().reset_index().sort_values(by="Percentage", ascending=False)
                    )
                    behavior_order = df_grouped_first["Unified Behavior"].tolist()
                    max_y = max(max_y, df_grouped_first["Percentage"].max())
                create_bar_chart(
                    df_filtered,
                    behavior_order=behavior_order,
                    color_map=color_map,
                    title=chart_title,
                    y_max=max_y,
                )
                download_filtered_data(df_filtered, key_prefix=f"field_{i}_")
            else:
                st.warning("No data available for the selected filters.")

    st.subheader("Comparison Report")
    comparison_df = pd.DataFrame()

    for i, (df_filtered, chart_title) in enumerate(comparison_data):
        if not df_filtered.empty:
            df_grouped = (
                df_filtered.groupby("Unified Behavior", observed=False)["Percentage"].mean().reset_index()
            )
            col_name = f"{chart_titles[i]} ({i+1})"
            if comparison_df.empty:
                comparison_df = df_grouped.set_index("Unified Behavior").rename(columns={"Percentage": col_name})
            else:
                comparison_df = comparison_df.join(
                    df_grouped.set_index("Unified Behavior")["Percentage"].rename(col_name),
                    how="outer",
                )

    if not comparison_df.empty:
        comparison_df = comparison_df.fillna(0).sort_values(by=comparison_df.columns[0], ascending=False)
        comparison_df.index.name = "Unified Behavior"
        for i in range(1, len(comparison_df.columns)):
            diff_col = f"Diff {i}-{i+1}"
            comparison_df[diff_col] = comparison_df.iloc[:, i] - comparison_df.iloc[:, i - 1]
        st.dataframe(comparison_df.reset_index())
        download_filtered_data(comparison_df.reset_index(), key_prefix="comparison_")
    else:
        st.warning("No data available for comparison.")


def main():
    df = load_data()
    if df.empty:
        st.error("Data could not be loaded.")
        return
    check_dataset_freshness(df)
    run(df)


if __name__ == "__main__":
    main()
