import numpy as np
import pandas as pd
import ezyquant as ez
from ezyquant.backtesting import Context

from src.utils import z_score


def get_valuation_metrics(
    ssc: ez.SETSignalCreator,
):
    pb = ssc.get_data(field="pb", timeframe="daily")
    pe = ssc.get_data(field="pe", timeframe="daily")

    # EV = Market Cap + Debt - Cash
    mkt_cap = ssc.get_data(field="mkt_cap", timeframe="daily")
    int_bearing_debt = ssc.get_data(field="int_bearing_debt", timeframe="yearly")
    cash = ssc.get_data(field="cash", timeframe="yearly")
    ev = mkt_cap + int_bearing_debt - cash

    ebitda = ssc.get_data(field="ebitda", timeframe="ytd")
    # EV/EBITDA
    ev_div_ebitda = ev / ebitda

    # FCF Yield (free_cash_flow = net_operating - net_investing, FCF Yield = free_cash_flow / market cap)
    net_operating = ssc.get_data(field="net_operating", timeframe="yearly")
    net_investing = ssc.get_data(field="net_investing", timeframe="yearly")
    free_cash_flow = net_operating - net_investing
    fcf_yield = free_cash_flow / mkt_cap

    return pb, pe, ev_div_ebitda, fcf_yield


def get_score(
    pb: pd.DataFrame,
    pe: pd.DataFrame,
    ev_div_ebitda: pd.DataFrame,
    fcf_yield: pd.DataFrame,
):
    return -z_score(pb) + -z_score(pe) + -z_score(ev_div_ebitda) + z_score(fcf_yield)


def _get_buy_signal(
    score_df: pd.DataFrame,
):
    # Long top 20%
    pct_rank = score_df.rank(axis=1, pct=True)
    buy_signal = pd.DataFrame(
        data=False, index=score_df.index, columns=score_df.columns
    )
    buy_signal[pct_rank >= 0.8] = True
    return buy_signal


def _get_sell_signal(
    score_df: pd.DataFrame,
):
    # Short bottom 20%
    pct_rank = score_df.rank(axis=1, pct=True)
    sell_signal = pd.DataFrame(
        data=False, index=score_df.index, columns=score_df.columns
    )
    sell_signal[pct_rank <= 0.2] = True
    return sell_signal


def _filter_signal(ssc: ez.SETSignalCreator, signal_df: pd.DataFrame):
    return ssc.screen_universe(signal_df)


def _rank_signal(
    ssc: ez.SETSignalCreator,
    signal_df: pd.DataFrame,
    score_df: pd.DataFrame,
):
    factor_df = score_df

    factor_df = pd.DataFrame(
        np.where((signal_df > 0), factor_df, np.nan),
        columns=factor_df.columns,
        index=factor_df.index,
    )

    POS_NUM = 20  # TODO: Remove magic number
    signal_df = ssc.rank(factor_df=score_df, quantity=POS_NUM, ascending=False)

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


def valuation_strategy(
    ssc: ez.SETSignalCreator,
):
    pb, pe, ev_div_ebitda, fcf_yield = get_valuation_metrics(ssc)
    score_df = get_score(pb, pe, ev_div_ebitda, fcf_yield)
    buy_signal_df = _get_buy_signal(
        score_df,
    )
    sell_signal_df = _get_sell_signal(
        score_df,
    )

    # TODO: Remove magic number
    signal_df = buy_signal_df.astype(int) + sell_signal_df.astype(int) * -10

    signal_df = _filter_signal(ssc, signal_df)
    signal_df = _rank_signal(ssc, signal_df, score_df)
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
