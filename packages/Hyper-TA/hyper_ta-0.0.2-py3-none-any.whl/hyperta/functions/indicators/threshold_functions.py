# === External libraries ===
import pandas as pd

from src.ta.functions.indicators.trend_indicators import *
from src.ta.functions.indicators.momentum_indicators import *
from src.ta.functions.indicators.volatility_indicators  import *
from src.ta.functions.indicators.universal_indicator_dispatcher import *


#----------------
#crossUpThresehold   1 indicator static level
#----------------
def crossUpThreshold(df, type, thr, period, wd=0, sell=False, **kwargs):
    """
    Detect cross-up or cross-down of indicator vs static threshold.
    Handles arbitrary indicator parameters via **kwargs.
    """

    # compute indicator with user-provided params
    ind_df = calculate_indicator(df.copy(), type=type, period=period, plot=False, **kwargs)

    # find the indicator column (everything except Date)
    col = [c for c in ind_df.columns if c != 'Date'][0]

    prev = ind_df[col].shift(1)
    curr = ind_df[col]

    # BUY: cross up through threshold
    if not sell:
        cross = (prev < thr) & (curr >= thr)

    # SELL: cross down through threshold
    else:
        cross = (prev > thr) & (curr <= thr)

    # Create signal column
    ind_df["signal"] = df["close"].where(cross, "")

    # Filter only signal rows
    signals = ind_df[ind_df["signal"] != ""][["Date", "signal"]].copy()

    # cluster filtering: remove signals too close to each other
    signals["diff"] = signals["Date"].diff().dt.days
    signals = signals[(signals["diff"].isna()) | (signals["diff"] > wd)]

    return signals.drop(columns="diff")





#----------------
#crossUpLineThresehold  2 indicators - line vs line
#----------------
def crossUpLineThreshold(df,type1, period1,type2, period2,wd=1,kwargs1={},kwargs2={}):
    """
    Detects clean cross-up events between two indicators (line-to-line crossover).
    Filters out duplicate consecutive signals so each cluster is represented once.

    Parameters:
        df (pd.DataFrame): Must contain full OHLCV + 'Date'
        type1 (str): First indicator type (e.g., 'ema')
        period1 (int): Period for indicator 1
        type2 (str): Second indicator type
        period2 (int): Period for indicator 2
        wd (int): Minimum gap (in days) between valid signals
        kwargs1 (dict): Extra arguments for indicator 1
        kwargs2 (dict): Extra arguments for indicator 2

    Returns:
        pd.DataFrame: ['Date', 'signal'] with clean cross-up entries
    """

    # === 1. Calculate both indicators
    ind1_df = calculate_indicator(df.copy(), type=type1, period=period1, plot=False, **kwargs1)
    ind2_df = calculate_indicator(df.copy(), type=type2, period=period2, plot=False, **kwargs2)

    # === 2. Standardize column names to 'value'
    ind1_df = ind1_df.rename(columns={col: 'value' for col in ind1_df.columns if col != 'Date'})
    ind2_df = ind2_df.rename(columns={col: 'value' for col in ind2_df.columns if col != 'Date'})

    # === 3. Merge with suffixes
    merged = pd.merge(ind1_df, ind2_df, on='Date', suffixes=('_1', '_2'))

    # === 4. Detect upward cross (value_1 crosses above value_2)
    cross_up = (merged['value_1'].shift(1) < merged['value_2'].shift(1)) & \
               (merged['value_1'] >= merged['value_2'])

    # === 5. Mark only exact crossing points
    merged['signal'] = cross_up.apply(lambda x: 'entry' if x else '')

    # === 6. Keep only rows with signals
    signals = merged[merged['signal'] != ''][['Date', 'signal']].copy()

    # === 7. Filter clusters: keep only first signal if multiple are close
    signals['diff'] = signals['Date'].diff().dt.days
    signals = signals[(signals['diff'].isna()) | (signals['diff'] > wd)]
    signals = signals.drop(columns='diff')

    return signals






#----------------
#In Range Threshold
# TODO: add wd!
#----------------
def inRangeThreshold(df,type,period,lower,upper,kwargs={}):
    """
    Detects when an indicator's value is inside a specified threshold range.
    Returns a signal for every candle that is inside the range.

    Parameters:
        df (pd.DataFrame): Input OHLCV with 'Date'
        type (str): Indicator type (e.g., 'rsi', 'williams', etc.)
        period (int): Indicator period
        lower (float): Lower threshold
        upper (float): Upper threshold
        kwargs (dict): Extra kwargs for the indicator

    Returns:
        pd.DataFrame: ['Date', 'signal'] rows where value is inside range
    """

    # === 1. Calculate indicator
    ind = calculate_indicator(df.copy(), type=type, period=period, plot=False, **kwargs)
    col = [c for c in ind.columns if c != 'Date'][0]
    ind = ind.rename(columns={col: 'value'})

    # === 2. Check if inside range
    in_range = (ind['value'] >= lower) & (ind['value'] <= upper)

    # === 3. Mark signals for every in-range candle
    ind['signal'] = in_range.apply(lambda x: 'entry' if x else '')

    # === 4. Return only signal rows
    result = ind[ind['signal'] != ''][['Date', 'signal']].copy()
    return result




#----------------
# Time Threshold (generalized)
#----------------
def timeThreshold(df,type,period,level,direction="above",min_candles=3,wd=0,**kwargs):  # "above" or "below"
    """
    Detects when an indicator has stayed above/below a threshold
    for at least N consecutive candles.

    Parameters:
        df (pd.DataFrame): OHLCV DataFrame
        type (str): Indicator type (e.g. 'rsi', 'ema', 'williams')
        period (int): Indicator period
        level (float): Threshold value
        direction (str): "above" or "below"
        min_candles (int): Required streak length
        wd (int): Expand signals ±wd candles
        kwargs (dict): Extra params for the indicator

    Returns:
        pd.DataFrame: ['Date', 'signal']
    """

    # === 1. Calculate indicator
    ind = calculate_indicator(df.copy(), type=type, period=period, plot=False, **kwargs)
    col = [c for c in ind.columns if c != "Date"][0]
    ind = ind.rename(columns={col: "value"})

    # === 2. Boolean mask above/below threshold
    if direction == "above":
        cond = ind["value"] > level
    elif direction == "below":
        cond = ind["value"] < level
    else:
        raise ValueError("direction must be 'above' or 'below'")

    # === 3. Count consecutive streaks
    streak = (cond != cond.shift()).cumsum()
    streak_count = cond.groupby(streak).cumsum()

    # === 4. Valid if streak length ≥ min_candles
    valid = streak_count >= min_candles

    # === 5. Expand by window if needed
    if wd > 0:
        for i in range(1, wd + 1):
            valid |= valid.shift(i)
            valid |= valid.shift(-i)

    # === 6. Build result
    signals = ind.loc[valid, ["Date"]].copy()
    signals["signal"] = "entry"

    return signals
