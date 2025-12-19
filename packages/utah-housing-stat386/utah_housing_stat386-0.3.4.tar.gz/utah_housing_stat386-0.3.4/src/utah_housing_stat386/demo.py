import pandas as pd
import pkg_resources


def load_demo_data():
    """
    Load the demo dataset included with the package

    Returns:
        pandas DataFrame: Demo housing data
    """
    try:
        # Try to load from package resources
        data_path = pkg_resources.resource_filename('utah_housing_stat386', 'data/test_data.csv')
        df = pd.read_csv(data_path)
        return df
    except:
        # Fallback to loading from GitHub
        url = 'https://raw.githubusercontent.com/sethfrand/Stat_386_final_project/refs/heads/main/data/test_data.csv'
        df = pd.read_csv(url)
        return df


def demo_cleaning():
    """
    Demonstrate the cleaning functions on demo data

    Returns:
        tuple: (raw_df, cleaned_df) - both raw and cleaned dataframes
    """
    from utah_housing_stat386.cleaning import clean_housing_data, remove_duplicates, remove_invalid_entries

    print("Loading demo data...")
    df_raw = load_demo_data()

    print("\n" + "=" * 50)
    print("RAW DATA SAMPLE")
    print("=" * 50)
    print(df_raw.head())
    print(f"\nShape: {df_raw.shape}")
    print(f"Columns: {df_raw.columns.tolist()}")

    print("\n" + "=" * 50)
    print("CLEANING DATA...")
    print("=" * 50)

    df_clean = clean_housing_data(df_raw)
    print("✓ Applied cleaning functions")

    df_clean = remove_invalid_entries(df_clean)
    print("✓ Removed invalid entries")

    df_clean = remove_duplicates(df_clean)
    print("✓ Removed duplicates")

    print("\n" + "=" * 50)
    print("CLEANED DATA SAMPLE")
    print("=" * 50)
    print(df_clean.head())
    print(f"\nShape: {df_clean.shape}")

    print("\n" + "=" * 50)
    print("DATA TYPES")
    print("=" * 50)
    print(df_clean.dtypes)

    print("\n" + "=" * 50)
    print("SUMMARY STATISTICS")
    print("=" * 50)
    print(df_clean.describe())

    return df_raw, df_clean


def run_demo():
    """
    Run a complete demo of the package functionality
    """
    print("=" * 60)
    print("UTAH HOUSING DATA PACKAGE DEMO")
    print("=" * 60)

    df_raw, df_clean = demo_cleaning()

    print("\n" + "=" * 60)
    print("DEMO COMPLETE!")
    print("=" * 60)
    print("\nYou can now:")
    print("1. Use get_data() to scrape live data")
    print("2. Use get_cleaned_data() to get cleaned data")
    print("3. Use cleaning functions individually on your data")
    print("\nExample:")
    print("  from utah_housing_stat386 import get_cleaned_data")
    print("  df = get_cleaned_data(max_listings=5, cities=['provo'])")