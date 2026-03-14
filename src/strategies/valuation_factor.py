import numpy as np
import pandas as pd
import ezyquant as ez


def get_valuation_metrics(
    ssc: ez.SETSignalCreator,
):
    pb = ssc.get_data(field="pb", timeframe="daily")
    pe = ssc.get_data(field="pe", timeframe="daily")

    # TODO: EV = Market Cap + Debt - Cash
    mkt_cap = ssc.get_data(field="mkt_cap", timeframe="daily")
    int_bearing_debt = ssc.get_data(field="int_bearing_debt", timeframe="yearly")
    cash = ssc.get_data(field="cash", timeframe="yearly")
    ev = mkt_cap + int_bearing_debt - cash

    ebitda = ssc.get_data(field="ebitda", timeframe="ytd")
    # TODO: EV/EBITDA
    ev_div_ebitda = ev / ebitda

    # TODO: FCF Yield (free_cash_flow = net_operating - net_investing, FCF Yield = free_cash_flow / market cap)
    net_operating = ssc.get_data(field="net_operating", timeframe="yearly")
    net_investing = ssc.get_data(field="net_investing", timeframe="yearly")
    free_cash_flow = net_operating - net_investing
    fcf_yield = free_cash_flow / mkt_cap

    return pb, pe, ev_div_ebitda, fcf_yield


def _get_buy_signal(
    ssc: ez.SETSignalCreator,
    close_df: pd.DataFrame,
    high_df: pd.DataFrame,
    low_df: pd.DataFrame,
):
    pass  # TODO


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
    pass  # TODO
    # # Calculate rate of change
    # factor_df = (close_df - close_df.shift(252)) / close_df.shift(252)

    # factor_df = pd.DataFrame(
    #     np.where((signal_df > 0), factor_df, np.nan),
    #     columns=factor_df.columns,
    #     index=factor_df.index,
    # )

    # POS_NUM = 20  # TODO: Remove magic number
    # signal_df = ssc.rank(factor_df=factor_df, quantity=POS_NUM, ascending=False)

    # return signal_df


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


def valuation_strategy(
    ssc: ez.SETSignalCreator,
):
    pass  # TODO
    # buy_signal_df = _get_buy_signal(ssc, close_df, high_df, low_df)
    # sell_signal_df = _get_sell_signal(ssc, close_df, high_df, low_df)

    # # TODO: Remove magic number
    # signal_df = buy_signal_df.astype(int) + sell_signal_df.astype(int) * -10

    # signal_df = _filter_signal(ssc, signal_df)
    # signal_df = _rank_signal(ssc, signal_df, close_df)
    # signal_df = _handle_sign_signal(ssc, signal_df)

    # return signal_df
