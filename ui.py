import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pandas.tseries.offsets import MonthEnd


def select_period(df, key_prefix=""):
    """Return a start and end ``pd.Timestamp`` based on user input."""
    min_date = df["Date"].min()
    max_date = df["Date"].max()

    years = range(min_date.year, max_date.year + 1)
    months = range(1, 13)

    use_range = st.checkbox(
        "Select date range", value=False, key=f"{key_prefix}use_range"
    )

    if use_range:
        col4, col5 = st.columns(2)
        with col4:
            start_year = st.selectbox(
                "Start Year",
                options=years,
                index=0,
                key=f"{key_prefix}start_year",
            )
            start_month = st.selectbox(
                "Start Month",
                options=months,
                format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
                index=min_date.month - 1,
                key=f"{key_prefix}start_month",
            )
        with col5:
            end_year = st.selectbox(
                "End Year",
                options=years,
                index=len(years) - 1,
                key=f"{key_prefix}end_year",
            )
            end_month = st.selectbox(
                "End Month",
                options=months,
                format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
                index=max_date.month - 1,
                key=f"{key_prefix}end_month",
            )

        start_date = pd.Timestamp(year=start_year, month=start_month, day=1)
        end_date = pd.Timestamp(year=end_year, month=end_month, day=1) + MonthEnd(1)

        if start_date > end_date:
            st.error("Start date cannot be after end date. Please select a valid range.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            selected_year = st.selectbox(
                "Year",
                options=years,
                index=len(years) - 1,
                key=f"{key_prefix}year",
            )
        with col2:
            selected_month = st.selectbox(
                "Month",
                options=months,
                format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
                index=max_date.month - 1,
                key=f"{key_prefix}month",
            )

        start_date = pd.Timestamp(year=selected_year, month=selected_month, day=1)
        end_date = start_date + MonthEnd(1)

    return start_date, end_date


def select_filters(df, key_prefix="", default_filter_option="By Individual"):
    """Return filters for the selected query type."""
    filter_option = st.selectbox(
        "Filter By",
        options=["By Individual", "By Sex and Social Group"],
        index=0 if default_filter_option == "By Individual" else 1,
        key=f"{key_prefix}filter_option",
    )

    if filter_option == "By Individual":
        animals = df["Focal Name"].unique()
        selected_animal = st.selectbox(
            "Select an Animal", options=animals, key=f"{key_prefix}animal"
        )
        selected_sex = None
        selected_groups = None
    else:
        sex_options = ["Male", "Female"]
        group_options = df["Social Group"].unique()

        selected_animal = None
        selected_sex = st.multiselect(
            "Select Sex",
            options=sex_options,
            default=sex_options,
            key=f"{key_prefix}sex",
        )
        selected_groups = st.multiselect(
            "Select Social Groups",
            options=group_options,
            default=list(group_options),
            key=f"{key_prefix}group",
        )

    return filter_option, selected_animal, selected_sex, selected_groups


def create_bar_chart(df_filtered, behavior_order=None, color_map=None, title="Activity Budget Distribution", y_max=None):
    """Display a bar chart for the provided data."""
    if behavior_order is not None:
        behavior_order = list(dict.fromkeys(behavior_order))
        df_filtered.loc[:, "Unified Behavior"] = pd.Categorical(
            df_filtered["Unified Behavior"], categories=behavior_order, ordered=True
        )

    df_grouped = (
        df_filtered.groupby("Unified Behavior", observed=False)["Percentage"].mean().reset_index().sort_values(by="Percentage", ascending=False)
    )

    if behavior_order is not None:
        df_grouped = df_grouped.sort_values(by="Percentage", ascending=False)

    fig = px.bar(
        df_grouped,
        x="Unified Behavior",
        y="Percentage",
        title=title,
        labels={"Percentage": "Percentage", "Unified Behavior": "Behavior"},
        template="plotly_dark",
        color="Unified Behavior",
        color_discrete_map=color_map,
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        yaxis=dict(range=[0, y_max]) if y_max else {},
    )

    st.plotly_chart(fig, use_container_width=True)


def create_deviation_bar_chart(deviations, title):
    """Draw a grouped bar chart of deviation values."""
    fig = go.Figure()

    colors = {"All": "#636EFA", "Group": "#EF553B", "Individual": "#00CC96"}

    for column in ["All", "Group", "Individual"]:
        fig.add_trace(
            go.Bar(
                x=deviations.index,
                y=deviations[column],
                name=column,
                marker_color=colors[column],
            )
        )

    fig.update_layout(
        title=title,
        barmode="group",
        xaxis_tickangle=-45,
        yaxis_title="Deviation (%)",
        template="plotly_dark",
        showlegend=True,
    )

    st.plotly_chart(fig, use_container_width=True)


def create_history_line_chart(df_line, title):
    """Display a time series line chart for behavior history."""
    if df_line.empty:
        st.warning("No data available for the selected options.")
        return

    df_line = df_line.sort_values("Date")
    df_line["Month"] = df_line["Date"].dt.to_period("M").astype(str)

    fig = px.line(
        df_line,
        x="Month",
        y="Percentage",
        markers=True,
        title=title,
        template="plotly_dark",
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Percentage")
    st.plotly_chart(fig, use_container_width=True)


def download_filtered_data(df_filtered, key_prefix=""):
    """Offer download buttons for CSV and Excel."""
    if df_filtered.empty:
        return
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    from io import BytesIO

    output = BytesIO()
    df_filtered.to_excel(output, index=False)

    csv_key = f"{key_prefix}csv" if key_prefix else "csv"
    excel_key = f"{key_prefix}excel" if key_prefix else "excel"

    col_csv, col_excel = st.columns(2)
    with col_csv:
        st.download_button(
            "Download CSV",
            data=csv,
            file_name="filtered_behavior.csv",
            mime="text/csv",
            key=csv_key,
        )
    with col_excel:
        st.download_button(
            "Download Excel",
            data=output.getvalue(),
            file_name="filtered_behavior.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=excel_key,
        )

    st.markdown(
        f"""
        <style>
        button[data-baseweb="button"]#{csv_key} {{
            background-color: #1f77b4;
            padding: 0.25rem 0.75rem;
            font-size: 0.8rem;
        }}
        button[data-baseweb="button"]#{excel_key} {{
            background-color: #2ca02c;
            padding: 0.25rem 0.75rem;
            font-size: 0.8rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
