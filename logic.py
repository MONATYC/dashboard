import pandas as pd


def filter_data(df, start_date, end_date, filter_option, animal=None, sexes=None, groups=None):
    """Return data filtered by date range and query options."""
    subset = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
    if filter_option == "By Individual" and animal:
        subset = subset[subset["Focal Name"] == animal]
    elif filter_option == "By Sex and Social Group":
        if sexes is not None:
            subset = subset[subset["Sex"].isin(sexes)]
        if groups is not None:
            subset = subset[subset["Social Group"].isin(groups)]
    return subset


def get_behavior_color_map(df):
    """Return a consistent color for each behavior."""
    behaviors = sorted(df["Unified Behavior"].unique())
    from plotly.colors import qualitative

    colors = qualitative.Plotly
    if len(behaviors) > len(colors):
        colors *= -(-len(behaviors) // len(colors))
    return {behavior: colors[i] for i, behavior in enumerate(behaviors)}


def calculate_deviations(df, df_filtered, selected_animal):
    """Compute deviation percentages for a single individual."""
    common_behaviors = df["Unified Behavior"].unique()

    all_mean = (
        df.groupby("Unified Behavior", observed=False)["Percentage"].mean().reindex(common_behaviors, fill_value=0)
    )
    group_mean = (
        df[df["Social Group"] == df_filtered["Social Group"].iloc[0]]
        .groupby("Unified Behavior", observed=False)["Percentage"].mean().reindex(common_behaviors, fill_value=0)
    )
    individual_mean_historical = (
        df[df["Focal Name"] == selected_animal]
        .groupby("Unified Behavior", observed=False)["Percentage"].mean().reindex(common_behaviors, fill_value=0)
    )
    individual_mean_selected = (
        df_filtered.groupby("Unified Behavior", observed=False)["Percentage"].mean().reindex(common_behaviors, fill_value=0)
    )

    deviations = pd.DataFrame(
        {
            "Percentage": individual_mean_selected,
            "Individual": individual_mean_selected - individual_mean_historical,
            "Group": individual_mean_selected - group_mean,
            "All": individual_mean_selected - all_mean,
        }
    ).fillna(0)

    return deviations.loc[:, :].sort_values(by="Percentage", ascending=False)


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
