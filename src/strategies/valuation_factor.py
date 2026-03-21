import numpy as np
import pandas as pd
import ezyquant as ez
from ezyquant.backtesting import Context


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
    ev_ebitda = ev / ebitda

    # FCF Yield (free_cash_flow = net_operating - net_investing, FCF Yield = free_cash_flow / market cap)
    net_operating = ssc.get_data(field="net_operating", timeframe="yearly")
    net_investing = ssc.get_data(field="net_investing", timeframe="yearly")
    free_cash_flow = net_operating - net_investing
    fcf_yield = free_cash_flow / mkt_cap

    return pb, pe, ev_ebitda, fcf_yield


def get_pb_score(ssc: ez.SETSignalCreator):
    # Lower PB = better
    pb = ssc.get_data(field="pb", timeframe="daily")
    return ((pb.mean() / pb).clip(lower=0.5, upper=1.2) - 0.5) / (1.2 - 0.5)


def get_pe_score(ssc: ez.SETSignalCreator):
    # Lower PE = better
    pe = ssc.get_data(field="pe", timeframe="daily")
    return ((pe.mean() / pe).clip(lower=0.5, upper=1.2) - 0.5) / (1.2 - 0.5)


def get_fcf_yield_score(ssc: ez.SETSignalCreator):
    # Higher free cash flow yield = better

    # FCF Yield (free_cash_flow = net_operating - net_investing, FCF Yield = free_cash_flow / market cap)
    mkt_cap = ssc.get_data(field="mkt_cap", timeframe="daily")
    net_operating = ssc.get_data(field="net_operating", timeframe="yearly")
    net_investing = ssc.get_data(field="net_investing", timeframe="yearly")
    free_cash_flow = net_operating - net_investing
    fcf_yield = free_cash_flow / mkt_cap

    return (fcf_yield / 0.04).clip(lower=0, upper=1)


def get_rsi_score(
    ssc: ez.SETSignalCreator,
    close_df: pd.DataFrame,
):
    rsi = ssc.ta.rsi(close_df, window=14)

    rsi_score = pd.DataFrame()
    for symbol in rsi.columns:
        rsi_score[symbol] = pd.cut(
            rsi[symbol],
            bins=[0, 30, 40, 50, 60, 70, float("inf")],
            labels=[1, 0.8, 0.6, 0.5, 0.4, 0.2],
        )
    return rsi_score.astype("float64")


def get_score(
    ssc: ez.SETSignalCreator,
    close_df: pd.DataFrame,
):
    WEIGHTS = {
        "PB_score": 4,
        "PE_score": 2,
        "FCF_score": 3,
        # "momentum_score": 4,
        "RSI_score": 3,
        # "dividend_score": 5,
    }

    # Calculate weighted total score
    score = get_pb_score(ssc) * WEIGHTS["PB_score"]
    score += get_pe_score(ssc) * WEIGHTS["PE_score"]
    score += get_fcf_yield_score(ssc) * WEIGHTS["FCF_score"]
    score += get_rsi_score(ssc, close_df) * WEIGHTS["RSI_score"]

    score /= sum(WEIGHTS.values())

    return score


def get_stop_loss(
    ssc: ez.SETSignalCreator,
    close_df: pd.DataFrame,
):
    ema_150_df = ssc.ta.ema(close_df, 150)
    ema_200_df = ssc.ta.ema(close_df, 200)
    stop_loss = ema_150_df < ema_200_df
    return stop_loss


def get_signal(ssc: ez.SETSignalCreator, close_df: pd.DataFrame):
    score = get_score(
        ssc,
        close_df,
    )
    # Top 20% = BUY, Bottom 20% = SELL
    signal = pd.DataFrame()
    for symbol in score.columns:
        signal[symbol] = pd.cut(
            score[symbol], bins=[0, 0.4, 0.8, 1.0], labels=["SELL", "HOLD", "BUY"]
        )

    stop_loss = get_stop_loss(ssc, close_df)
    for symbol in score.columns:
        signal[symbol][stop_loss[symbol]] = "SELL"

    return signal


def get_backtest_algorithm(pos_num=20):
    def backtest_algorithm(c: Context):
        if c.volume == 0 and c.signal == "BUY":
            return c.target_pct_port(1 / pos_num)  # Buy
        elif c.volume > 0 and c.signal == "SELL":
            return c.target_pct_port(0)  # Sell
        else:
            return 0  # Do nothing

    return backtest_algorithm
