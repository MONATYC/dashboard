import pandas as pd
from app import get_behavior_history, get_behavior_history_by_filters


def test_get_behavior_history():
    data = {
        "Date": ["2021-02", "2021-01"],
        "Focal Name": ["Bongo", "Bongo"],
        "Unified Behavior": ["Play", "Play"],
        "Percentage": [20, 10],
    }
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])

    result = get_behavior_history(df, "Bongo", "Play")
    dates = list(result["Date"].dt.strftime("%Y-%m"))
    assert dates == ["2021-01", "2021-02"]
    assert list(result["Percentage"]) == [10, 20]


def test_get_behavior_history_by_filters():
    data = {
        "Date": ["2021-01", "2021-01", "2021-02", "2021-02"],
        "Focal Name": ["A", "B", "A", "B"],
        "Unified Behavior": ["Play", "Play", "Play", "Play"],
        "Percentage": [10, 20, 30, 40],
        "Sex": ["Male", "Female", "Male", "Female"],
        "Social Group": ["G1", "G1", "G1", "G1"],
    }
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])

    result = get_behavior_history_by_filters(
        df, sexes=["Male", "Female"], groups=["G1"], behavior="Play"
    )
    dates = list(result["Date"].dt.strftime("%Y-%m"))
    assert dates == ["2021-01", "2021-02"]
    assert list(result["Percentage"]) == [15, 35]
