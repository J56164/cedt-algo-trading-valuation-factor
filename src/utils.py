import pandas as pd
from pathlib import Path


def get_moving_average(data: pd.DataFrame, window: int):
    return data.rolling(window).mean()


def z_score(df):
    # Z-score across columns (stocks) for each date
    return (df - df.mean()) / df.std()


def find_project_root(marker: str = "pyproject.toml") -> Path:
    current = Path(__file__).resolve()  # or Path.cwd() in notebooks
    for parent in [current, *current.parents]:
        if (parent / marker).exists():
            return parent
    raise FileNotFoundError(f"Project root marker '{marker}' not found")
