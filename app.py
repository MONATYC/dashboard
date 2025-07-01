import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pandas.tseries.offsets import MonthEnd
from data_utils import load_data, check_dataset_freshness

# Configure the Streamlit page
st.set_page_config(
    page_title="Chimpanzee Behavior Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Function to select the time period
def select_period(df, key_prefix=""):
    """Return a start and end ``pd.Timestamp`` based on user input.

    Parameters
    ----------
    df : pandas.DataFrame
        Loaded dataset with a ``Date`` column.
    key_prefix : str, optional
        Prefix for widget keys when multiple selectors are displayed.
    """
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
                "Start Year", options=years, key=f"{key_prefix}start_year"
            )
            start_month = st.selectbox(
                "Start Month",
                options=months,
                format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
                key=f"{key_prefix}start_month",
            )
        with col5:
            end_year = st.selectbox(
                "End Year", options=years, key=f"{key_prefix}end_year"
            )
            end_month = st.selectbox(
                "End Month",
                options=months,
                format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
                key=f"{key_prefix}end_month",
            )

        start_date = pd.Timestamp(year=start_year, month=start_month, day=1)
        end_date = pd.Timestamp(year=end_year, month=end_month, day=1) + MonthEnd(1)

        # Validate that the start date is not after the end date
        if start_date > end_date:
            st.error(
                "Start date cannot be after end date. Please select a valid range."
            )
    else:
        col1, col2 = st.columns(2)
        with col1:
            selected_year = st.selectbox(
                "Year", options=years, index=0, key=f"{key_prefix}year"
            )
        with col2:
            selected_month = st.selectbox(
                "Month",
                options=months,
                format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
                index=0,
                key=f"{key_prefix}month",
            )

        start_date = pd.Timestamp(year=selected_year, month=selected_month, day=1)
        end_date = start_date + MonthEnd(1)

    return start_date, end_date


# Function to select filters with mutual exclusivity
def select_filters(df, key_prefix=""):
    """Return filters for the selected query type.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset to provide selection options from.
    key_prefix : str, optional
        Prefix for widget keys when used multiple times.

    Returns
    -------
    tuple
        (filter_option, selected_animal, selected_sex, selected_groups)
    """
    filter_option = st.selectbox(
        "Filter By",
        options=["By Individual", "By Sex and Social Group"],
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


# Function to create a consistent color map for behaviors
def get_behavior_color_map(df):
    """Return a consistent color for each behavior."""
    behaviors = sorted(df["Unified Behavior"].unique())
    colors = px.colors.qualitative.Plotly
    if len(behaviors) > len(colors):
        # Extend colors if there are more behaviors than colors
        colors *= -(  # Ceiling division to ensure full coverage
            -len(behaviors) // len(colors)
        )
    color_map = {behavior: colors[i] for i, behavior in enumerate(behaviors)}
    return color_map


# Function to create the bar chart with consistent behavior colors
def create_bar_chart(
    df_filtered,
    behavior_order=None,
    color_map=None,
    title="Activity Budget Distribution",
    y_max=None,
):
    """Display a bar chart for the provided data."""
    # Ensure the behavior_order contains unique values
    if behavior_order is not None:
        behavior_order = list(
            dict.fromkeys(behavior_order)
        )  # Remove duplicates while preserving order
        df_filtered.loc[:, "Unified Behavior"] = pd.Categorical(
            df_filtered["Unified Behavior"], categories=behavior_order, ordered=True
        )

    df_grouped = (
        df_filtered.groupby("Unified Behavior", observed=False)["Percentage"]
        .mean()
        .reset_index()
        .sort_values(by="Percentage", ascending=False)
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


# New function to calculate deviations
def calculate_deviations(df, df_filtered, selected_animal):
    """Compute deviation percentages for a single individual."""
    common_behaviors = df["Unified Behavior"].unique()

    # Media de todos los individuos para cada conducta en la base de datos completa
    all_mean = (
        df.groupby("Unified Behavior", observed=False)["Percentage"]
        .mean()
        .reindex(common_behaviors, fill_value=0)
    )

    # Media del grupo social del individuo seleccionado para cada conducta
    group_mean = (
        df[df["Social Group"] == df_filtered["Social Group"].iloc[0]]
        .groupby("Unified Behavior", observed=False)["Percentage"]
        .mean()
        .reindex(common_behaviors, fill_value=0)
    )

    # Media histórica del individuo seleccionado para cada conducta
    individual_mean_historical = (
        df[df["Focal Name"] == selected_animal]
        .groupby("Unified Behavior", observed=False)["Percentage"]
        .mean()
        .reindex(common_behaviors, fill_value=0)
    )

    # Media de las conductas para el individuo en la fecha o rango de fechas seleccionadas
    individual_mean_selected = (
        df_filtered.groupby("Unified Behavior", observed=False)["Percentage"]
        .mean()
        .reindex(common_behaviors, fill_value=0)
    )

    # Calcular las desviaciones
    deviations = pd.DataFrame(
        {
            "Percentage": individual_mean_selected,
            "Individual": individual_mean_selected - individual_mean_historical,
            "Group": individual_mean_selected - group_mean,
            "All": individual_mean_selected - all_mean,
        }
    ).fillna(0)

    # Ordenar la tabla por la columna 'Percentage' de mayor a menor
    deviations = deviations.loc[:, :].sort_values(by="Percentage", ascending=False)

    return deviations


# New function to create deviation bar chart
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


def get_behavior_history(df, animal, behavior):
    """Return behavior percentages for a specific animal over time."""
    subset = df[(df["Focal Name"] == animal) & (df["Unified Behavior"] == behavior)]
    return subset.sort_values("Date")[["Date", "Percentage"]]


def get_behavior_history_by_filters(df, sexes=None, groups=None, behavior=None):
    """Return mean behavior percentages over time filtered by sex/group."""
    subset = df[df["Unified Behavior"] == behavior]
    if sexes is not None:
        subset = subset[subset["Sex"].isin(sexes)]
    if groups is not None:
        subset = subset[subset["Social Group"].isin(groups)]

    grouped = subset.groupby("Date", as_index=False)["Percentage"].mean()
    return grouped.sort_values("Date")[["Date", "Percentage"]]


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
    """Offer download buttons for CSV and Excel.

    Parameters
    ----------
    df_filtered : pd.DataFrame
        The data to download.
    key_prefix : str, optional
        Prefix used to create unique keys for Streamlit widgets.
    """
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


# Main function
def main():
    """Render the dashboard UI."""
    st.sidebar.title("Dashboard Settings")
    st.sidebar.write("Use the following options to customize the data visualization.")

    # Load data
    df = load_data()
    if df.empty:
        st.error("Data could not be loaded.")
        return
    check_dataset_freshness(df)

    # Generate a consistent color map for behaviors
    behavior_color_map = get_behavior_color_map(df)

    # Option to select the type of query
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
        # Snapshot view
        start_date, end_date = select_period(df)
        filter_option, selected_animal, selected_sex, selected_groups = select_filters(
            df
        )

        # Filter data according to selection
        if filter_option == "By Individual" and selected_animal:
            df_filtered = df[
                (df["Date"] >= start_date)
                & (df["Date"] <= end_date)
                & (df["Focal Name"] == selected_animal)
            ]
            chart_title = f"Behavior Dashboard for {selected_animal}"
        elif filter_option == "By Sex and Social Group":
            sex_filter = (
                df.index if selected_sex is None else df["Sex"].isin(selected_sex)
            )
            group_filter = (
                df.index
                if selected_groups is None
                else df["Social Group"].isin(selected_groups)
            )

            df_filtered = df[
                (df["Date"] >= start_date)
                & (df["Date"] <= end_date)
                & sex_filter
                & group_filter
            ]

            sex_text = ", ".join(selected_sex) if selected_sex else "All Sexes"
            group_text = (
                ", ".join(selected_groups) if selected_groups else "All Social Groups"
            )
            chart_title = (
                f"Behavior Dashboard by Sex: {sex_text} | Social Groups: {group_text}"
            )
        else:
            df_filtered = pd.DataFrame()
            chart_title = "Behavior Dashboard"

        if not df_filtered.empty:
            st.title(chart_title)
            st.subheader("Activity Budget Distribution")

            # Ensure snapshot is sorted by Percentage descendingly
            df_filtered_sorted = df_filtered.sort_values(
                by="Percentage", ascending=False
            )
            create_bar_chart(
                df_filtered_sorted.sort_values(by="Percentage", ascending=False),
                behavior_order=df_filtered_sorted["Unified Behavior"].tolist(),
                color_map=behavior_color_map,
                title="Activity Budget Distribution",
                y_max=df_filtered_sorted["Percentage"].max(),
            )
            download_filtered_data(df_filtered_sorted, key_prefix="filtered_")

            # Calculate deviations
            if filter_option == "By Individual" and selected_animal:
                deviations = calculate_deviations(df, df_filtered, selected_animal)

                # Create deviation bar chart
                create_deviation_bar_chart(deviations, "Behavior Deviations")

                # Display deviation table
                st.subheader("Deviation Summary")
                st.dataframe(
                    deviations[["Percentage", "Individual", "Group", "All"]]
                    .style.format(
                        na_rep="-",
                        formatter={
                            col: "{:.2f}"
                            if pd.api.types.is_numeric_dtype(deviations[col])
                            else "{}"
                            for col in deviations.columns
                        },
                    )
                    .map(
                        lambda x: "color: lightblue"
                        if pd.to_numeric(x, errors="coerce") > 0
                        else "color: orange"
                        if pd.to_numeric(x, errors="coerce") < 0
                        else ""
                    )
                )

        else:
            st.warning("No data available for the selected filters.")

    elif query_type == "Comparison":
        # Comparison view
        num_fields = st.sidebar.selectbox(
            "Number of Comparison Fields", [2, 3, 4], index=0
        )
        st.title("Behavior Comparison Dashboard")

        # Create columns for each comparison field
        columns = st.columns(num_fields)

        # To store the maximum Y value across all charts
        max_y = 0
        comparison_data = []
        chart_titles = []  # New list to store chart titles

        # First pass to gather data and determine max_y
        for i in range(num_fields):
            with columns[i]:
                key_prefix = f"field_{i}_"

                start_date, end_date = select_period(df, key_prefix=key_prefix)
                filter_option, selected_animal, selected_sex, selected_groups = (
                    select_filters(df, key_prefix=key_prefix)
                )

                # Filter data according to selection
                if filter_option == "By Individual" and selected_animal:
                    df_filtered = df[
                        (df["Date"] >= start_date)
                        & (df["Date"] <= end_date)
                        & (df["Focal Name"] == selected_animal)
                    ]
                    chart_title = f"{selected_animal} | {start_date.strftime('%B %Y')} - {end_date.strftime('%B %Y')}"
                elif filter_option == "By Sex and Social Group":
                    sex_filter = (
                        df.index
                        if selected_sex is None
                        else df["Sex"].isin(selected_sex)
                    )
                    group_filter = (
                        df.index
                        if selected_groups is None
                        else df["Social Group"].isin(selected_groups)
                    )

                    df_filtered = df[
                        (df["Date"] >= start_date)
                        & (df["Date"] <= end_date)
                        & sex_filter
                        & group_filter
                    ]

                    sex_text = ", ".join(selected_sex) if selected_sex else "All Sexes"
                    group_text = (
                        ", ".join(selected_groups)
                        if selected_groups
                        else "All Social Groups"
                    )
                    date_text = (
                        f"{start_date.strftime('%B %Y')} - {end_date.strftime('%B %Y')}"
                        if start_date != end_date
                        else start_date.strftime("%B %Y")
                    )
                    chart_title = (
                        f"Sex: {sex_text} | Groups: {group_text} | Dates: {date_text}"
                    )
                else:
                    df_filtered = pd.DataFrame()
                    chart_title = "Behavior Comparison"

                chart_titles.append(chart_title)  # Store the chart title
                st.subheader(chart_title)  # Use the chart title as the subheader

                if not df_filtered.empty:
                    df_grouped = (
                        df_filtered.groupby("Unified Behavior", observed=False)[
                            "Percentage"
                        ]
                        .mean()
                        .reset_index()
                    )
                    current_max = df_grouped["Percentage"].max()
                    if current_max > max_y:
                        max_y = current_max
                    comparison_data.append((df_filtered, chart_title))
                else:
                    comparison_data.append((pd.DataFrame(), chart_title))

        # Second pass to create charts with consistent Y-axis
        behavior_order = None
        for i in range(num_fields):
            df_filtered, chart_title = comparison_data[i]
            with columns[i]:
                if not df_filtered.empty:
                    # For the first chart, determine behavior order
                    if i == 0:
                        df_grouped_first = (
                            df_filtered.groupby("Unified Behavior", observed=False)[
                                "Percentage"
                            ]
                            .mean()
                            .reset_index()
                            .sort_values(by="Percentage", ascending=False)
                        )
                        behavior_order = df_grouped_first["Unified Behavior"].tolist()
                        # Update max_y if needed
                        max_y = max(max_y, df_grouped_first["Percentage"].max())
                    else:
                        df_grouped = (
                            df_filtered.groupby("Unified Behavior", observed=False)[
                                "Percentage"
                            ]
                            .mean()
                            .reset_index()
                        )
                        df_grouped = df_grouped.sort_values(
                            by="Percentage", ascending=False
                        )

                    create_bar_chart(
                        df_filtered,
                        behavior_order=behavior_order,
                        color_map=behavior_color_map,
                        title=chart_title,
                        y_max=max_y,
                    )
                    download_filtered_data(df_filtered, key_prefix=f"field_{i}_")
                else:
                    st.warning("No data available for the selected filters.")

        # Create comparison report
        st.subheader("Comparison Report")
        comparison_df = pd.DataFrame()

        for i, (df_filtered, chart_title) in enumerate(comparison_data):
            if not df_filtered.empty:
                df_grouped = (
                    df_filtered.groupby("Unified Behavior", observed=False)[
                        "Percentage"
                    ]
                    .mean()
                    .reset_index()
                )
                if comparison_df.empty:
                    comparison_df = df_grouped.set_index("Unified Behavior").rename(
                        columns={"Percentage": chart_titles[i]}
                    )
                else:
                    comparison_df = comparison_df.join(
                        df_grouped.set_index("Unified Behavior")["Percentage"].rename(
                            chart_titles[i]
                        ),
                        how="outer",
                    )

        if not comparison_df.empty:
            comparison_df = comparison_df.fillna(0).sort_values(
                by=comparison_df.columns[0], ascending=False
            )
            # Ensure the index name is set to 'Unified Behavior'
            comparison_df.index.name = "Unified Behavior"
            # Ensure the index name is set to 'Unified Behavior'
            comparison_df.index.name = "Unified Behavior"

            # Calculate differences
            for i in range(1, len(comparison_df.columns)):
                diff_col = f"Diff {i}-{i+1}"
                comparison_df[diff_col] = (
                    comparison_df.iloc[:, i] - comparison_df.iloc[:, i - 1]
                )

            # Display comparison table with formatting
            st.dataframe(
                comparison_df.reset_index()
                .style.format(
                    na_rep="-",
                    formatter={
                        col: "{:.2f}%"
                        if pd.api.types.is_numeric_dtype(comparison_df[col])
                        else "{}"
                        for col in comparison_df.columns
                    },
                )
                .set_properties(**{"text-align": "left", "color": "white"})
                .map(
                    lambda x: "color: lightblue"
                    if x > 0
                    else "color: orange"
                    if x < 0
                    else "",
                    subset=[
                        col for col in comparison_df.columns if col.startswith("Diff")
                    ],
                )
                .set_properties(**{"color": "white"}, subset=["Unified Behavior"])
            )
            download_filtered_data(comparison_df.reset_index(), key_prefix="comparison_")
        else:
            st.warning("No data available for comparison.")

    elif query_type == "Behavior History":
        st.title("Behavior History")

        filter_option, sel_animal, sel_sex, sel_groups = select_filters(df, key_prefix="history_")
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

    else:
        st.warning("Please select a query type.")


# Run the main function
if __name__ == "__main__":
    main()
