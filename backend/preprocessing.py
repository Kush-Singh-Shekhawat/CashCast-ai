import pandas as pd

def preprocess_data(df):
    """
    Cleans and preprocesses the input DataFrame.

    Steps:
    - Converts 'date' column to datetime
    - Sorts DataFrame by date (ascending)
    - Fills missing values in income/expense columns with 0
    - Ensures numeric types for income/expense columns

    Parameters:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: Cleaned DataFrame
    """

    df = df.copy()

    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Ensure numeric types and fill missing values
    numeric_cols = ["income_pre_tax", "income_post_tax", "expense"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Sort by date ascending
    df = df.sort_values(by="date", ascending=True)

    return df

    if len(df) < 3:
        raise ValueError("Not enough data for analysis (minimum 3 rows required)")