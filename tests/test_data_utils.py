import pandas as pd
from data_utils import load_data


def test_load_data(tmp_path, monkeypatch):
    csv_path = tmp_path / "behavior.csv"
    csv_path.write_text("Date,Focal Name,Unified Behavior,Percentage\n2024-01,Chimp,Play,10")

    df = load_data(path=str(csv_path))
    assert not df.empty
    assert list(df.columns) == [
        "Date",
        "Focal Name",
        "Unified Behavior",
        "Percentage",
    ]
    assert pd.api.types.is_datetime64_any_dtype(df["Date"])
