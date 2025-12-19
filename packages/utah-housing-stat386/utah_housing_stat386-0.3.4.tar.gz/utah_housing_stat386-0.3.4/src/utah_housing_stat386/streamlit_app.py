"""Enhanced Streamlit app for STAT 386 Utah Housing Data Analysis."""

from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

try:
    from cleaning import cleaned_static_data, clean_housing_data, remove_duplicates, remove_invalid_entries
except ImportError:
    st.error("Could not import cleaning module. Make sure cleaning.py is in the same directory.")
    st.stop()


@st.cache_data
def load_static_data():
    """Load and cache the cleaned housing data."""
    try:
        # Load directly from GitHub URLs
        df1 = pd.read_csv(
            'https://raw.githubusercontent.com/carsonordyna/Stat_386_final_project/refs/heads/main/data/utah_housing_data_ORIGINAL.csv')
        df2 = pd.read_csv(
            'https://raw.githubusercontent.com/carsonordyna/Stat_386_final_project/refs/heads/main/data/Salt_Lake_County_housing_data.csv')
        df_raw = pd.concat([df1, df2])

        # Apply cleaning
        df_clean = clean_housing_data(df_raw)
        df_clean = remove_invalid_entries(df_clean)
        df_clean = remove_duplicates(df_clean)

        return df_clean
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def clean_uploaded_data(df):
    """Apply cleaning pipeline to uploaded data."""
    df_clean = clean_housing_data(df)
    df_clean = remove_invalid_entries(df_clean)
    df_clean = remove_duplicates(df_clean)
    return df_clean


def create_price_distribution(df):
    """Create price distribution histogram."""
    fig = px.histogram(
        df,
        x='price',
        nbins=50,
        title='Distribution of Housing Prices',
        labels={'price': 'Price ($)', 'count': 'Number of Homes'},
        color_discrete_sequence=['#1f77b4']
    )
    fig.update_layout(showlegend=False)
    return fig


def create_price_by_city(df):
    """Create box plot of prices by city."""
    fig = px.box(
        df,
        x='city',
        y='price',
        title='Price Distribution by City',
        labels={'city': 'City', 'price': 'Price ($)'}
    )
    fig.update_layout(xaxis_tickangle=45)
    return fig


def create_price_per_sqft_scatter(df):
    """Create scatter plot of price vs square footage."""
    df_filtered = df.dropna(subset=['sqft', 'price'])
    df_filtered = df_filtered[df_filtered['sqft'] > 0]
    df_filtered['price_per_sqft'] = df_filtered['price'] / df_filtered['sqft']

    fig = px.scatter(
        df_filtered,
        x='sqft',
        y='price',
        color='city',
        title='Price vs Square Footage',
        labels={'sqft': 'Square Feet', 'price': 'Price ($)', 'city': 'City'},
        hover_data=['beds', 'baths', 'price_per_sqft']
    )
    return fig


def create_beds_baths_analysis(df):
    """Create analysis of beds and baths."""
    df_filtered = df.dropna(subset=['beds', 'baths'])

    grouped = df_filtered.groupby(['beds', 'baths']).agg({
        'price': 'mean',
        'mls': 'count'
    }).reset_index()
    grouped.columns = ['beds', 'baths', 'avg_price', 'count']

    fig = px.scatter(
        grouped,
        x='beds',
        y='baths',
        size='count',
        color='avg_price',
        title='Average Price by Beds and Baths',
        labels={'beds': 'Bedrooms', 'baths': 'Bathrooms',
                'avg_price': 'Average Price ($)', 'count': 'Number of Listings'},
        color_continuous_scale='Viridis'
    )
    return fig


def create_year_built_analysis(df):
    """Analyze price trends by year built."""
    df_filtered = df.dropna(subset=['year_built', 'price'])
    df_filtered = df_filtered[df_filtered['year_built'] > 1900]

    grouped = df_filtered.groupby('year_built').agg({
        'price': 'mean',
        'mls': 'count'
    }).reset_index()
    grouped.columns = ['year_built', 'avg_price', 'count']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=grouped['year_built'],
        y=grouped['avg_price'],
        mode='lines+markers',
        name='Average Price',
        yaxis='y1'
    ))

    fig.update_layout(
        title='Average Home Price by Year Built',
        xaxis_title='Year Built',
        yaxis_title='Average Price ($)',
        hovermode='x unified'
    )
    return fig


def display_summary_stats(df):
    """Display summary statistics."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Listings", f"{len(df):,}")

    with col2:
        avg_price = df['price'].mean()
        st.metric("Average Price", f"${avg_price:,.0f}")

    with col3:
        median_price = df['price'].median()
        st.metric("Median Price", f"${median_price:,.0f}")

    with col4:
        total_cities = df['city'].nunique()
        st.metric("Cities Covered", total_cities)


def main() -> None:
    st.set_page_config(page_title="Utah Housing Data Analysis", layout="wide")
    st.title("🏠 Utah Housing Market Analysis")
    st.write(
        "Interactive analysis of Utah housing data from Utah and Salt Lake Counties. "
        "Explore price distributions, city comparisons, and market trends."
    )

    # Sidebar controls
    with st.sidebar:
        st.header("🔧 Data Source")
        dataset_choice = st.selectbox("Dataset", ["Static Data", "Upload CSV"])

        apply_cleaning = st.checkbox("Apply cleaning pipeline to uploaded data", value=True)

        st.header("🔍 Filters")

    # Load data based on selection
    if dataset_choice == "Static Data":
        with st.spinner('Loading housing data...'):
            df = load_static_data()
    else:
        uploaded = st.sidebar.file_uploader("Upload a CSV file", type="csv")
        if uploaded:
            df_raw = pd.read_csv(uploaded)
            if apply_cleaning:
                with st.spinner('Cleaning uploaded data...'):
                    df = clean_uploaded_data(df_raw)
                st.sidebar.success("✓ Data cleaned successfully!")
            else:
                df = df_raw
        else:
            st.info("No file uploaded yet. Falling back to static data so the widgets stay live.")
            df = load_static_data()

    if df is None or len(df) == 0:
        st.error("Failed to load data. Please check your data sources.")
        return

    # Sidebar filters (continued)
    with st.sidebar:
        # City filter
        cities = ['All'] + sorted(df['city'].dropna().unique().tolist())
        selected_city = st.selectbox("Select City", cities)

        # Price range filter
        if df['price'].notna().any():
            min_price, max_price = st.slider(
                "Price Range ($)",
                min_value=int(df['price'].min()),
                max_value=int(df['price'].max()),
                value=(int(df['price'].min()), int(df['price'].max())),
                format="$%d"
            )
        else:
            min_price = 0
            max_price = 1000000

        # Beds filter
        if df['beds'].notna().any():
            min_beds = int(df['beds'].min())
            max_beds = int(df['beds'].max())
            beds_range = st.slider("Bedrooms", min_beds, max_beds, (min_beds, max_beds))
        else:
            beds_range = (0, 10)
        #year_build filter
        if df['year_built'].notna().any():
            min_year = int(df['year_built'].min())
            max_year = int(df['year_built'].max())
            year_range = st.slider("Year Built", min_year, max_year, (min_year, max_year))
        # Baths filter
        if df['baths'].notna().any():
            min_baths = int(df['baths'].min())
            max_baths = int(df['baths'].max())
            baths_range = st.slider("Bathrooms", min_baths, max_baths, (min_baths, max_baths))
        else:
            baths_range = (0, 10)


        # Analysis options
        st.header("📊 Analysis Options")
        show_raw_data = st.checkbox("Show Raw Data Table")
        show_stats = st.checkbox("Show Statistical Summary", value=True)

    # Apply filters
    df_filtered = df.copy()
    if selected_city != 'All':
        df_filtered = df_filtered[df_filtered['city'] == selected_city]
    df_filtered = df_filtered[
        (df_filtered['price'] >= min_price) &
        (df_filtered['price'] <= max_price)
        ]
    if df_filtered['beds'].notna().any():
        df_filtered = df_filtered[
            (df_filtered['beds'] >= beds_range[0]) &
            (df_filtered['beds'] <= beds_range[1])
            ]
    if df_filtered['baths'].notna().any():
        df_filtered = df_filtered[
            (df_filtered['baths'] >= baths_range[0]) &
            (df_filtered['baths'] <= baths_range[1])
            ]
    if df_filtered['year_built'].notna().any():
        df_filtered = df_filtered[
            (df_filtered['year_built'] >= year_range[0]) &
            (df_filtered['year_built'] <= year_range[1])
            ]

    # Display data preview
    st.subheader("📋 Data Preview")
    st.dataframe(df_filtered.head(10), use_container_width=True)

    # Display summary statistics
    st.subheader("📈 Key Metrics")
    display_summary_stats(df_filtered)

    # Main visualizations
    st.subheader("📊 Price Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(create_price_distribution(df_filtered), use_container_width=True)

    with col2:
        if selected_city == 'All':
            st.plotly_chart(create_price_by_city(df_filtered), use_container_width=True)
        else:
            # Show price per sqft for single city
            df_temp = df_filtered.dropna(subset=['sqft', 'price'])
            if len(df_temp) > 0:
                df_temp = df_temp[df_temp['sqft'] > 0]
                df_temp['price_per_sqft'] = df_temp['price'] / df_temp['sqft']
                fig = px.histogram(
                    df_temp,
                    x='price_per_sqft',
                    title=f'Price per Sq Ft in {selected_city.title()}',
                    labels={'price_per_sqft': 'Price per Sq Ft ($)'}
                )
                st.plotly_chart(fig, use_container_width=True)

    st.subheader("🏘️ Property Characteristics")

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(create_price_per_sqft_scatter(df_filtered), use_container_width=True)

    with col2:
        st.plotly_chart(create_beds_baths_analysis(df_filtered), use_container_width=True)

    # Year built analysis
    st.subheader("📅 Historical Trends")
    st.plotly_chart(create_year_built_analysis(df_filtered), use_container_width=True)

    # Statistical summary
    if show_stats:
        st.subheader("📋 Statistical Summary")

        numeric_cols = ['price', 'beds', 'baths', 'sqft', 'year_built', 'lot_size', 'garage']
        available_cols = [col for col in numeric_cols if col in df_filtered.columns]

        st.dataframe(df_filtered[available_cols].describe(), use_container_width=True)

    # Raw data table
    if show_raw_data:
        st.subheader("🗂️ Raw Data")
        st.dataframe(df_filtered, use_container_width=True)

        # Download button
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="utah_housing_filtered.csv",
            mime="text/csv"
        )

    # Footer
    st.markdown("---")
    st.info(
        "💡 **Tips**: Use the sidebar to switch between static data and uploaded CSV. "
        "Apply filters to explore specific cities and price ranges. "
        "Hover over charts for detailed information. Enable 'Show Raw Data' to view and download the data."
    )


if __name__ == "__main__":
    main()