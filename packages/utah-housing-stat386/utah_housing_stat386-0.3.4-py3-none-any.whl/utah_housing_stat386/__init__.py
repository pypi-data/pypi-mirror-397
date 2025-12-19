from utah_housing_stat386.core import get_data
from utah_housing_stat386.cleaning import (
    get_cleaned_data,
    clean_housing_data,
    clean_price,
    clean_numeric_field,
    clean_year_built,
    clean_lot_size,
    clean_garage,
    remove_duplicates,
    remove_invalid_entries
)
from utah_housing_stat386.demo import load_demo_data, demo_cleaning, run_demo

__version__ = "0.3.2"

__all__ = [
    "get_data",
    "get_cleaned_data",
    "clean_housing_data",
    "clean_price",
    "clean_numeric_field",
    "clean_year_built",
    "clean_lot_size",
    "clean_garage",
    "remove_duplicates",
    "remove_invalid_entries",
    "load_demo_data",
    "demo_cleaning",
    "run_demo"
]