import ezyquant as ez
from ezyquant.backtesting import Context


def get_backtest_algorithm(pos_num: int):
    def backtest_algorithm(c: Context):
        if c.volume == 0 and c.signal > 0:
            return c.target_pct_port(1 / pos_num)  # Buy
        elif c.volume > 0 and c.signal < 0:
            return c.target_pct_port(0)  # Sell
        else:
            return 0  # Do nothing

    return backtest_algorithm


def backtest(signal_df, start_date):
    pass
