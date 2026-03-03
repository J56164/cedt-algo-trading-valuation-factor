import pandas as pd


def get_moving_average(data: pd.DataFrame, window: int):
    return data.rolling(window).mean()
