import pandas as pd
from app import get_behavior_history


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
