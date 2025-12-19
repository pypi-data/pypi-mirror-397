import pandas as pd
import re
import numpy as np
from datetime import datetime


def check_is_nan(value):
    """Check if value is NaN or empty."""
    if pd.isnull(value) or value == "":
        return True
    return False


def clean_price(price_str):
    """
    Cleaning the price to display as a numeric value instead of string.

    Args:
        price_str: str - string representation of the price
    Returns:
        float: Numerical value of the price
    """
    if check_is_nan(price_str):
        return np.nan

    clean = re.sub(r'[$,\s]', '', str(price_str))
    try:
        return float(clean)
    except:
        return np.nan


def clean_numeric_field(value):
    """
    Convert other numeric string fields to numeric values

    Args:
        value (str): string value of the field

    Returns:
        float: numeric value of the field or NaN if invalid
    """
    if check_is_nan(value):
        return np.nan

    cleaned = re.sub(r'[,\s]', '', str(value))
    try:
        return float(cleaned)
    except ValueError:
        return np.nan


def clean_year_built(year_built):
    """
    Validate and clean the year built column

    Args:
        year_built: String representation of the year built

    Returns:
        int: valid year built or NaN
    """
    if check_is_nan(year_built):
        return np.nan

    try:
        year = int(year_built)
        current_year = datetime.now().year
        if 1800 <= year <= current_year + 2:
            return year
        return np.nan
    except ValueError:
        return np.nan


def clean_lot_size(lot_size_str):
    """
    Clean the lot size field to return numeric value in acres

    Args:
        lot_size_str: str - string representation of the lot size

    Returns:
        float: Numeric value of the lot size in acres
    """
    if check_is_nan(lot_size_str):
        return np.nan

    lot_size_str = str(lot_size_str).lower().strip()

    numbers = re.findall(r'[\d.]+', lot_size_str)
    if not numbers:
        return np.nan

    value = float(numbers[0])

    if 'ac' in lot_size_str or 'acre' in lot_size_str:
        return value
    elif 'sq' in lot_size_str or 'ft' in lot_size_str:
        # An acre is 43,560 sq ft
        return value / 43560
    else:
        # Assume acres if no unit specified
        return value


def clean_garage(garage_str):
    """
    Extracting the number of garages

    Args:
        garage_str: string representation of the garage

    Returns:
        int: number of garages or 0 if none/invalid
    """
    if check_is_nan(garage_str):
        return 0

    numbers = re.findall(r'\d+', str(garage_str))
    if numbers:
        if int(numbers[0]) <= 15:
            return int(numbers[0])
        else:
            return 0
    return 0


def clean_address(address_str):
    """
    Standardize the address column

    Args:
        address_str: String representation of the address

    Returns:
        str: cleaned address string
    """
    if check_is_nan(address_str):
        return np.nan

    cleaned = re.sub(r'\s+', ' ', str(address_str)).strip()
    cleaned = re.sub(r',\s*,', ',', cleaned)
    cleaned = cleaned.strip(',').strip()

    return cleaned


def clean_city(city_str):
    """
    Clean and standardize city names

    Args:
        city_str: String representation of the city

    Returns:
        str: cleaned city string
    """
    if check_is_nan(city_str):
        return np.nan
    return str(city_str).lower().strip()


def clean_housing_data(df):
    """
    Apply all cleaning functions to the dataframe

    Args:
        df: pandas DataFrame with the raw housing data

    Returns:
        pandas DataFrame with cleaned data
    """
    df_clean = df.copy()

    # Drop agent column if it exists
    if 'agent' in df_clean.columns:
        df_clean = df_clean.drop(columns=['agent'])

    # Clean numeric fields
    if 'price' in df_clean.columns:
        df_clean['price'] = df_clean['price'].apply(clean_price)

    if 'beds' in df_clean.columns:
        df_clean['beds'] = df_clean['beds'].apply(clean_numeric_field)

    if 'baths' in df_clean.columns:
        df_clean['baths'] = df_clean['baths'].apply(clean_numeric_field)

    if 'sqft' in df_clean.columns:
        df_clean['sqft'] = df_clean['sqft'].apply(clean_numeric_field)

    if 'year_built' in df_clean.columns:
        df_clean['year_built'] = df_clean['year_built'].apply(clean_year_built)

    if 'lot_size' in df_clean.columns:
        df_clean['lot_size'] = df_clean['lot_size'].apply(clean_lot_size)

    if 'garage' in df_clean.columns:
        df_clean['garage'] = df_clean['garage'].apply(clean_garage)

    if 'address' in df_clean.columns:
        df_clean['address'] = df_clean['address'].apply(clean_address)

    if 'city' in df_clean.columns:
        df_clean['city'] = df_clean['city'].apply(clean_city)

    return df_clean


def remove_duplicates(df, subset=['mls']):
    """
    Remove duplicate entries from the dataframe using the MLS number as the unique identifier

    Args:
        df: Pandas DataFrame with housing data
        subset: List of columns to check for duplicates

    Returns:
        pandas DataFrame: DataFrame with duplicates removed
    """
    return df.drop_duplicates(subset=subset, keep='first')


def remove_invalid_entries(df):
    """
    Remove rows with critical missing data

    Args:
        df: Pandas DataFrame with housing data

    Returns:
        pandas DataFrame: DataFrame with invalid entries removed
    """
    critical_fields = ['mls', 'price', 'address']

    for field in critical_fields:
        if field in df.columns:
            df = df[df[field].notna()]
            if field == 'price':
                df = df[df['price'] > 0]

    return df


def get_cleaned_data(max_listings=5, cities=None, output='pandas'):
    """
    Get housing data and apply cleaning automatically

    Args:
        max_listings (int): Maximum number of listings to fetch per city
        cities (list): List of cities to scrape (None = all cities)
        output (str): 'pandas' or 'csv'

    Returns:
        pandas DataFrame or str: Cleaned housing data or path to saved CSV
    """
    from utah_housing_stat386.core import get_data

    df_raw = get_data(max_listings=max_listings, cities=cities, output='pandas')

    df_clean = clean_housing_data(df_raw)
    df_clean = remove_invalid_entries(df_clean)
    df_clean = remove_duplicates(df_clean)

    if output == 'pandas':
        return df_clean
    elif output == 'csv':
        df_clean.to_csv("utah_housing_data_cleaned.csv", index=False)
        return "Data saved to utah_housing_data_cleaned.csv"
    else:
        raise ValueError("Invalid output option. Choose 'pandas' or 'csv'.")


def data_no_scape():
    """
    Get static housing data

    Returns:
        pandas DataFrame
    """
    #df1 = pd.read_csv("../../data/utah_housing_data_ORIGINAL.csv")
    #df2 = pd.read_csv("../../data/Salt_Lake_County_housing_data.csv")
    df1 = pd.read_csv('https://raw.githubusercontent.com/carsonordyna/Stat_386_final_project/refs/heads/main/data/utah_housing_data_ORIGINAL.csv')
    df2 = pd.read_csv('https://raw.githubusercontent.com/carsonordyna/Stat_386_final_project/refs/heads/main/data/Salt_Lake_County_housing_data.csv')

    return pd.concat([df1, df2])


def cleaned_static_data():
    """
    Get static housing data and apply cleaning automatically

    Args:
        max_listings (int): Maximum number of listings to fetch per city
        cities (list): List of cities to scrape (None = all cities)
        output (str): 'pandas' or 'csv'

    Returns:
        pandas DataFrame or str: Cleaned housing data or path to saved CSV
    """
    from utah_housing_stat386.core import get_data

    df_raw = data_no_scape()

    df_clean = clean_housing_data(df_raw)
    df_clean = remove_invalid_entries(df_clean)
    df_clean = remove_duplicates(df_clean)

    return df_clean

