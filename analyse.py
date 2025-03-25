import pandas as pd

df = pd.read_csv("redfin_listings.csv")

def inspect_data(df):
    print(df.head())
    print(df.info())
    print(df.describe())
    print(df.isnull().sum())

inspect_data(df)


import numpy as np

def clean_data(df):
    print("Cleaning data...")

    df = df.replace({'-': np.nan, 'N/A': np.nan, '': np.nan}, inplace=True)

    df = df.dropna(subset=['price', 'address', 'beds', 'baths', 'sqft'], inplace=True)

    df.reset_index(drop=True, inplace=True)

    print(f"Data cleaned: {len(df)} rows remaining.")
    return df
df = clean_data(df)


def handle_missing_geo(df):
    missing_geo = df[(df['latitude'].isnull()) | (df['longitude'].isnull())]
    if not missing_geo.empty:
        print(f"\nWarning: {len(missing_geo)} rows with missing latitude/longitude.")
        df = df.dropna(subset=['latitude', 'longitude'])
        print(f"{len(df)} rows remaining after dropping missing latitude/longitude.")
    return df

import re

def extract_numeric(value):
    """Extracts numeric values from a string. Handles cases like '1 bed', '2 baths', 'Studio'."""
    if isinstance(value, str):
        match = re.search(r'\d+', value)  # Find first numeric value
        return float(match.group()) if match else np.nan
    return np.nan

def convert_columns(df):
    print("Converting columns...")

    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    df['price'] = df['price'].str.replace('[$,]', '', '', regex=True).replace('', np.nan).astype(float)

    df['beds'] = df['beds'].apply(extract_numeric)
    df['baths'] = df['baths'].apply(extract_numeric)

    df['sqft'] = df['sqft'].replace(['—', '', 'N/A'], np.nan)
    df['sqft'] = df['sqft'].str.replace(',', '', regex=True)
    df['sqft'] = pd.to_numeric(df['sqft'], errors='coerce')

    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    print("Columns converted.")
    return df

df = convert_columns(df)

def summarize_data(df):
    print("\nSummary Statistics:")
    print(df.describe())

summarize_data(df)