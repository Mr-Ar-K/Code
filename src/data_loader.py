<<<<<<< HEAD
import pandas as pd
import numpy as np
import os

def load_historical_data(file_path):
    """
    Load historical data from a CSV file.

    Parameters:
    file_path (str): Path to the CSV file.

    Returns:
    pd.DataFrame: Loaded data or None if an error occurs.
    """
    try:
        data = pd.read_csv(file_path)
        print("Historical data loaded successfully.")
        return data
    except Exception as e:
        print(f"Error loading historical data: {e}")
        return None

def analyze_historical_data(data):
    """
    Analyze historical data and provide a summary.

    Parameters:
    data (pd.DataFrame): Data to analyze.

    Returns:
    pd.DataFrame: Summary statistics or None if an error occurs.
    """
    try:
        summary = data.describe(include='all')
        print("Data Analysis Summary:")
        print(summary)
        return summary
    except Exception as e:
        print(f"Error analyzing historical data: {e}")
        return None

def filter_data_by_criteria(data, criteria):
    """
    Filter data based on given criteria.

    Parameters:
    data (pd.DataFrame): Data to filter.
    criteria (str): Query string to filter data.

    Returns:
    pd.DataFrame: Filtered data or None if an error occurs.
    """
    try:
        filtered_data = data.query(criteria)
        print(f"Filtered data based on criteria: {criteria}")
        return filtered_data
    except Exception as e:
        print(f"Error filtering data: {e}")
        return None

def save_filtered_data(filtered_data, filename='data/filtered_data.csv'):
    """
    Save filtered data to a CSV file.

    Parameters:
    filtered_data (pd.DataFrame): Data to save.
    filename (str): Path to save the CSV file.

    Returns:
    None
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        filtered_data.to_csv(filename, index=False)
        print(f"Filtered data saved to {filename}")
    except Exception as e:
=======
import pandas as pd
import numpy as np
import os

def load_historical_data(file_path):
    """
    Load historical data from a CSV file.

    Parameters:
    file_path (str): Path to the CSV file.

    Returns:
    pd.DataFrame: Loaded data or None if an error occurs.
    """
    try:
        data = pd.read_csv(file_path)
        print("Historical data loaded successfully.")
        return data
    except Exception as e:
        print(f"Error loading historical data: {e}")
        return None

def analyze_historical_data(data):
    """
    Analyze historical data and provide a summary.

    Parameters:
    data (pd.DataFrame): Data to analyze.

    Returns:
    pd.DataFrame: Summary statistics or None if an error occurs.
    """
    try:
        summary = data.describe(include='all')
        print("Data Analysis Summary:")
        print(summary)
        return summary
    except Exception as e:
        print(f"Error analyzing historical data: {e}")
        return None

def filter_data_by_criteria(data, criteria):
    """
    Filter data based on given criteria.

    Parameters:
    data (pd.DataFrame): Data to filter.
    criteria (str): Query string to filter data.

    Returns:
    pd.DataFrame: Filtered data or None if an error occurs.
    """
    try:
        filtered_data = data.query(criteria)
        print(f"Filtered data based on criteria: {criteria}")
        return filtered_data
    except Exception as e:
        print(f"Error filtering data: {e}")
        return None

def save_filtered_data(filtered_data, filename='data/filtered_data.csv'):
    """
    Save filtered data to a CSV file.

    Parameters:
    filtered_data (pd.DataFrame): Data to save.
    filename (str): Path to save the CSV file.

    Returns:
    None
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        filtered_data.to_csv(filename, index=False)
        print(f"Filtered data saved to {filename}")
    except Exception as e:
>>>>>>> 52ce655ce85126d4f7249c6c512f79f7223f613b
        print(f"Error saving filtered data: {e}")