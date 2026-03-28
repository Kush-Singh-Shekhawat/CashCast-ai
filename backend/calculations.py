import pandas as pd

def calculate_metrics(df, initial_capital):
    """
    Calculates financial metrics on the DataFrame.

    Steps:
    - Creates 'net_cash_flow' = income_post_tax - expense
    - Creates 'cumulative_cash' as running total starting from initial_capital

    Parameters:
        df (pd.DataFrame): Input DataFrame
        initial_capital (float): Starting cash amount

    Returns:
        pd.DataFrame: DataFrame with added metrics
    """

    df = df.copy()

    # Net cash flow
    df["net_cash_flow"] = df["income_post_tax"] - df["expense"]

    # Cumulative cash (running total + initial capital)
    df["cumulative_cash"] = df["net_cash_flow"].cumsum() + initial_capital

    return df

    if initial_capital <= 0:
        raise ValueError("Initial capital must be greater than 0")    