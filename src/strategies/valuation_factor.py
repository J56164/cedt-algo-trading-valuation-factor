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


def valuation_strategy(
    ssc: ez.SETSignalCreator,
):
    pass
