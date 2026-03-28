import pandas as pd

def load_data(file):
    """
    Reads a CSV file, validates required columns, and returns a DataFrame.

    Parameters:
        file (str): Path to the CSV file

    Returns:
        pd.DataFrame: Validated DataFrame

    Raises:
        ValueError: If required columns are missing
        FileNotFoundError: If file does not exist
        pd.errors.EmptyDataError: If file is empty
    """
    # Read CSV
    df = pd.read_csv(file)

    # Required columns
    required_columns = {"date", "income_pre_tax", "income_post_tax", "expense"}

    # Validate columns
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    return df