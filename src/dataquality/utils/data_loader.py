import pandas as pd


def load_data_as_pd(file_path):
    """
    Load data from CSV or other formats.
    """
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None
