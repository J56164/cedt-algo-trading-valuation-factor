import numpy as np
import pandas as pd
import ezyquant as ez
from ezyquant.backtesting import Context


def _get_buy_signal(
    ssc: ez.SETSignalCreator,
    close_df: pd.DataFrame,
    high_df: pd.DataFrame,
    low_df: pd.DataFrame,
):
    ema_50_df = ssc.ta.ema(close_df, 50)
    ema_150_df = ssc.ta.ema(close_df, 150)
    ema_200_df = ssc.ta.ema(close_df, 200)

    (
        dc_252_high_df,
        dc_252_low_df,
        dc_252_middle_df,
        dc_252_percentage_df,
        dc_252_band_width_df,
    ) = ssc.ta.dc(high_df, low_df, close_df, 252)

    rsi_14_df = ssc.ta.rsi(close_df, 14)

    # 1. The current stock price is above both the 150-day (30-week)
    # and the 200-day (40-week) moving average price lines.
    price_above_150 = close_df > ema_150_df
    buy_signal_df = price_above_150.copy()

    price_above_200 = close_df > ema_200_df
    buy_signal_df &= price_above_200

    # 2. The 150-day moving average is above the 200-day moving average.
    buy_signal_df &= ema_150_df > ema_200_df

    # 3. The 200-day moving average line is trending up for at least 1 month
    # (preferably 4-5 months minimum in most cases).
    buy_signal_df &= price_above_200.rolling(20).apply(all) == 1

    # 4. The 50-day (10-week) moving average is above both the 150-day
    # and 200-day moving averages.
    buy_signal_df &= (ema_50_df > ema_150_df) & (ema_50_df > ema_200_df)

    # 5. The current stock price is trading above the 50-day moving average.
    buy_signal_df &= close_df > ema_50_df

    # 6. The current stock price is at least 30 percent above its 52-week low.
    # (Many of the best selections will be 100 percent, 300 percent, or greater
    # above their 52-week low before they emerge from a solid consolidation period
    # and mount a large scale advance.)
    buy_signal_df &= (close_df / dc_252_low_df) >= 1.3

    # 7. The current stock price is within at least 25 percent of its 52-week high
    # (the closer to a new high the better).
    buy_signal_df &= (close_df / dc_252_high_df) >= 0.75

    # 8. The relative strength ranking (as reported in Investor's Business Daily)
    # is no less than 70, and preferably in the 80s or 90s, which will
    # generally be the case with the better selections.
    buy_signal_df &= rsi_14_df >= 70

    return buy_signal_df


def _get_sell_signal(
    ssc: ez.SETSignalCreator,
    close_df: pd.DataFrame,
    high_df: pd.DataFrame,
    low_df: pd.DataFrame,
):
    ema_20_df = ssc.ta.ema(close_df, 20)

    # Sell when the current stock price is lower than 20-day moving average
    sell_signal_df = close_df < ema_20_df

    return sell_signal_df


def _filter_signal(ssc: ez.SETSignalCreator, signal_df: pd.DataFrame):
    return ssc.screen_universe(signal_df)


def _rank_signal(
    ssc: ez.SETSignalCreator, signal_df: pd.DataFrame, close_df: pd.DataFrame
):
    # Calculate rate of change
    factor_df = (close_df - close_df.shift(252)) / close_df.shift(252)

    factor_df = pd.DataFrame(
        np.where((signal_df > 0), factor_df, np.nan),
        columns=factor_df.columns,
        index=factor_df.index,
    )

    POS_NUM = 20  # TODO: Remove magic number
    signal_df = ssc.rank(factor_df=factor_df, quantity=POS_NUM, ascending=False)

    return signal_df


# TODO: Rename function
def _handle_sign_signal(ssc: ez.SETSignalCreator, signal_df: pd.DataFrame):
    lookahead_signal = ssc.screen_universe(signal_df, mask_value=-1).shift(
        -2
    )  # TODO: Remove magic number

    signal_df = pd.DataFrame(
        np.where((lookahead_signal == -1), -1, signal_df),
        columns=signal_df.columns,
        index=signal_df.index,
    )

    return signal_df


def trend_template(
    ssc: ez.SETSignalCreator,
    close_df: pd.DataFrame,
    high_df: pd.DataFrame,
    low_df: pd.DataFrame,
):
    buy_signal_df = _get_buy_signal(ssc, close_df, high_df, low_df)
    sell_signal_df = _get_sell_signal(ssc, close_df, high_df, low_df)

    # TODO: Remove magic number
    signal_df = buy_signal_df.astype(int) + sell_signal_df.astype(int) * -10

    signal_df = _filter_signal(ssc, signal_df)
    signal_df = _rank_signal(ssc, signal_df, close_df)
    signal_df = _handle_sign_signal(ssc, signal_df)

    return signal_df


def get_backtest_algorithm(pos_num: int):
    def backtest_algorithm(c: Context):
        if c.volume == 0 and c.signal > 0:
            return c.target_pct_port(1 / pos_num)  # Buy
        elif c.volume > 0 and c.signal < 0:
            return c.target_pct_port(0)  # Sell
        else:
            return 0  # Do nothing

    return backtest_algorithm
