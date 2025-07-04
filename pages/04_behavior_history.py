import streamlit as st
from data_utils import load_data, check_dataset_freshness
from logic import (
    get_behavior_history,
    get_behavior_history_by_filters,
)
from ui import select_filters, create_history_line_chart

st.set_page_config(
    page_title="\ud83d\udcc8 Behavior History",
    layout="wide",
    initial_sidebar_state="expanded",
)


def run(df):
    """Render the behavior history page."""
    filter_option, sel_animal, sel_sex, sel_groups = select_filters(
        df,
        key_prefix="history_",
        default_filter_option="By Sex and Social Group",
        style="radio",
    )
    behaviors = df["Unified Behavior"].unique()
    selected_behavior = st.selectbox("Select Behavior", behaviors, key="history_behavior")

    if filter_option == "By Individual" and sel_animal:
        df_line = get_behavior_history(df, sel_animal, selected_behavior)
        title = f"{selected_behavior} over time for {sel_animal}"
    else:
        df_line = get_behavior_history_by_filters(
            df,
            sexes=sel_sex,
            groups=sel_groups,
            behavior=selected_behavior,
        )
        sex_text = ", ".join(sel_sex) if sel_sex else "All Sexes"
        group_text = ", ".join(sel_groups) if sel_groups else "All Social Groups"
        title = f"{selected_behavior} over time | Sex: {sex_text} | Group: {group_text}"

    create_history_line_chart(df_line, title)

    if not df_line.empty and len(df_line) > 1:
        last = df_line.iloc[-1]["Percentage"]
        prev = df_line.iloc[-2]["Percentage"]
        delta = last - prev
        trend = "increased" if delta >= 0 else "decreased"
        st.info(
            f"{selected_behavior} {trend} {abs(delta):.1f}% since the previous month."
        )
    else:
        st.info("Not enough data for insights.")


def main():
    df = load_data()
    if df.empty:
        st.error("Data could not be loaded.")
        return
    check_dataset_freshness(df)
    run(df)


if __name__ == "__main__":
    main()
