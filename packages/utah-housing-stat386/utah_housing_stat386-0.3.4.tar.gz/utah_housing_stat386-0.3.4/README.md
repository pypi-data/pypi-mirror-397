
If you are interested in running through a tutorial or reading the documentation, you can go [here](https://carsonordyna.github.io/Stat_386_final_project/)

# **STAT 386 Final Project: Utah Housing Data Scraper**

## **Overview**

This project is a Python package designed to collect and analyze Utah housing data from UtahRealEstate.com. It focuses on properties in **Utah County** and **Salt Lake County**, providing structured data as well as tools for cleaning, visualization, and analysis.

The package's web scraper uses **Playwright** for browser automation and easy integration into other Python projects.

***

## **Features**

*   Scrapes housing listings for multiple cities in Utah
*   Extracts details such as:
    *   MLS number
    *   Price
    *   Address
    *   Beds, Baths, Square Footage
    *   Year Built, Lot Size, Garage
    *   Listing Agent
*   Outputs data as:
    *   **Pandas DataFrame** or
    *   **CSV file**
*   Configurable:
    *   Number of listings per city
    *   Target cities

***

## **Project Structure**

    Stat_386_final_project/
    ├── LICENSE
    ├── README.md
    ├── Documentation.qmd
    ├── Tutorial.qmd
    ├── TechnicalReport.qmd
    ├── index.qmd
    ├── pyproject.toml
    ├── streamlit_page.py
    ├── styles.css
    ├── uv.lock
    ├── data/
    │   ├── Salt_Lake_County_housing_data.csv
    │   ├── test_data.csv
    │   └── utah_housing_data_ORIGINAL.csv
    ├── scripts/
    │   ├── _scraper_less_intensive.py
    │   ├── salt_lake_county.py
    │   └── scraper.py
    ├── src/
    │   └── utah_housing_stat386/
    │       ├── __init__.py
    │       ├── core.py
    │       ├── cleaning.py
    │       ├── demo.py
    │       ├── data/
    │       └── streamlit_app.py
    ├── tests/
    │   ├── package_test.py
    │   ├── test_cleaning.py
    │   └── test.ipynb
    └── docs/
        └── (generated Quarto HTML files)

***

## **Package**

The main package is `utah_housing_stat386`, located in the `src/utah_housing_stat386/` directory. It contains the core functionality for scraping, cleaning, and data handling.

*   `core.py`: Contains the main scraping logic and data fetching functions
*   `cleaning.py`: Data cleaning and validation functions for housing data
*   `demo.py`: Demo functions for testing and quick prototyping
*   `__init__.py`: Initializes the package and exposes all public functions

***

## **Installation**

1.  **Install Playwright browsers** (required for scraping):
    ```bash
    pip install playwright
    playwright install
    ```
    This will download the necessary browser binaries (Chromium, Firefox, WebKit) for Playwright.

***

## **Usage**

The main functionality is exposed via the `get_data` function in `utah_housing_stat386.core`, which scrapes data directly. **Warning: This function is extremely memory instensive.** If static data is sufficient, it is easiest—**highly recommneded**—to simply use the `data_no_scape` function instead.

### **Example: Basic Data Fetching**

```python
# Import dependencies
from utah_housing_stat386.core import get_data
from utah_housing_stat386.cleaning import data_no_scape
import pandas as pd
import nest_asyncio
nest_asyncio.apply()


#####  Dynamic scraping  #####

# Fetch data for specific cities, 5 listings per city, return as DataFrame
df = get_data(max_listings=5, cities=['provo', 'salt-lake-city'], output="pandas")
print(df.head())

# Save data to CSV file instead instead
get_data(max_listings=5, output="csv")


#####  Static data (RECOMMENDED)  #####
df_static = data_no_scape()
```

***

## **Configuration**

*   **max\_listings**: Number of listings per city (default: 5)
*   **cities**: List of cities (default: all supported cities)
*   **output**: `"pandas"` DataFrame or `"csv"` file (default: `"pandas"`)

Supported cities include:

*   **Utah County**: alpine, american-fork, eagle-mountain, highland, lindon, lehi, orem, provo, saratoga-springs, spanish-fork
*   **Salt Lake County**: draper, holladay, midvale, millcreek, cottonwood-heights, murray, salt-lake-city, sandy, south-jordan, south-salt-lake, sugarhouse, west-jordan, west-valley

***

## **Data Files**

*   `data/utah_housing_data_ORIGINAL.csv`: Sample of scraped data for Utah County
*   `data/Salt_Lake_County_housing_data.csv`: Sample of scraped data for Salt Lake County
*   `data/test_data.csv`: Test dataset (produced in development)

## **Scripts (produced in development)**

*  `scripts/scraper.py`: Main scraper script using Playwright
*  `scripts/_scraper_less_intensive.py`: Less intensive version of the scraper
*  `scripts/salt_lake_county.py`: Script to scrape Salt Lake County data

## **Other Files & Resources**

*  `pyproject.toml`: Project configuration, dependencies, and package metadata
*  `uv.lock`: Lock file for reproducible dependency management
*  `streamlit_page.py`: Interactive Streamlit web interface for data exploration
*  `Tutorial.qmd`: User guide and tutorial for the package
*  `TechnicalReport.qmd`: Detailed technical documentation and methodology
*  `tests/`: Unit tests and integration tests for the package
*  `docs/`: Pre-built Quarto HTML documentation files

***

## **Data Cleaning**

The package includes comprehensive data cleaning functions to transform raw scraped data into analysis-ready format.

### **Quick Start with Cleaned Data**
```python
from utah_housing_stat386 import get_cleaned_data, cleaned_static_data

# Get cleaned data directly (via scraping, memory-intensive)
df_clean = get_cleaned_data(max_listings=10, output="pandas")
print(df_clean.head())

# Get static data (highly recommended)
df_static_clean = cleaned_static_data()
print(df_static_clean.head())
```

### **Manual Cleaning Workflow**
```python
from utah_housing_stat386.cleaning import data_no_scape
from utah_housing_stat386 import get_data, clean_housing_data, remove_duplicates, remove_invalid_entries

# Get raw data (statically)
df_raw = data_no_scape()

# Apply cleaning step-by-step
df_clean = clean_housing_data(df_raw)
df_clean = remove_duplicates(df_clean)
df_clean = remove_invalid_entries(df_clean)
```

### **Individual Cleaning Functions**
```python
from utah_housing_stat386 import clean_price, clean_lot_size, clean_garage

# Clean specific fields
df['price'] = df['price'].apply(clean_price)
df['lot_size'] = df['lot_size'].apply(clean_lot_size)  # Converts to acres
df['garage'] = df['garage'].apply(clean_garage)  # Extracts garage spaces
```

### **Cleaning Functions Reference**

| Function | Description | Example Input | Example Output |
|----------|-------------|---------------|----------------|
| `clean_price()` | Converts price strings to numeric | "$481,999" | 481999.0 |
| `clean_numeric_field()` | Cleans beds, baths, sqft | "1,252" | 1252.0 |
| `clean_year_built()` | Validates year built | "1919" | 1919 |
| `clean_lot_size()` | Converts to acres | "0.10 Ac" | 0.1 |
| `clean_garage()` | Extracts garage spaces | "2 Car" | 2 |
| `clean_housing_data()` | Applies all cleaning | DataFrame | Cleaned DataFrame |
| `remove_duplicates()` | Removes duplicate listings | DataFrame | Deduplicated DataFrame |
| `remove_invalid_entries()` | Removes rows with missing critical data | DataFrame | Filtered DataFrame |
| `check_is_nan()` | Checks whether a value is NaN or empty | None / "" | `True` / `False` |
| `clean_address()` | Standardizes and trims address strings | "123 Main St,, " | "123 Main St" |
| `clean_city()` | Normalizes city names to lowercase and trims whitespace | " Provo " | "provo" |
| `get_cleaned_data()` | Fetches data (via `get_data`), applies cleaning and returns DataFrame or writes CSV | `get_cleaned_data(max_listings=5)` | Cleaned DataFrame or path to CSV |
| `data_no_scape()` | Loads the bundled static CSV files and concatenates them into a DataFrame | n/a | DataFrame |
| `cleaned_static_data()` | Loads static CSVs and returns a cleaned DataFrame (applies cleaning pipeline) | n/a | Cleaned DataFrame |

## **Demo & Testing**

The package includes demo functionality to get started quickly:

```python
from utah_housing_stat386 import run_demo, demo_cleaning, load_demo_data

# Run full demo with sample data
run_demo()

# Load demo dataset
df_demo = load_demo_data()

# See demo cleaning in action
demo_cleaning()
```

Tests are located in the `tests/` directory and can be run with:
```bash
pytest tests/
```

## **License**

MIT 2025

***
