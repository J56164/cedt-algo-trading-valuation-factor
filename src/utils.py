import pandas as pd


def get_moving_average(data: pd.DataFrame, window: int):
    return data.rolling(window).mean()


def z_score(df):
    # Z-score across columns (stocks) for each date
    return (df - df.mean()) / df.std()
