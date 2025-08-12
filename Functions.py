import pandas as pd
import ast
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
import requests
import datetime
import numpy as np
import sqlite3

'''Web scraping function to fetch laptop data from Amazon using SerpAPI'''

SERPAPI_API_KEY='b04c1583667c674b9ad3e4d4eec73436b1415f8acfda3d2bafb365a97f51a8c2'

def web_scraping():
    params = {
        "api_key": SERPAPI_API_KEY,
        "engine": "amazon",
        "k": "laptop",
        "page": 1
    }

    all_results = []

    while True:
        try:
            response = requests.get("https://serpapi.com/search", params=params).json()

            organic_results = response.get("organic_results", [])
            if not organic_results:
                print("No more results found.")
                break

            all_results.extend(organic_results)
            print(f"Page {params['page']} processed.")

            params['page'] += 1 

        except Exception as e:
            print(f"Error on page {params['page']}: {e}")
            break

    
    df = pd.DataFrame(all_results)
    df['scrape_date'] = datetime.date.today()
    df.to_csv("amazon_scrape_data.csv", index=False)
    print("Scraping complete. Data saved to 'amazon_scrape_data.csv'.")


df=pd.read_csv('amazon_scrape_data.csv')

'''cleaning functions for the scraped data'''

def clean_delivery(col):
    try:
        return str(col)[2:15]
    except:
        return "Info not available"

def change_datatype(df):
    df['extracted_price'] = df['extracted_price'].astype(float)
    df['rating'] = df['rating'].astype(float)
    df['reviews'] = df['reviews'].astype(float)
    df['scrape_date'] = pd.to_datetime(df['scrape_date'])
    return df

def parse_specs(spec_str):
    DEFAULT_KEYS = ['display_size', 'ram', 'disk_size', 'operating_system']
    try:
        spec_dict = ast.literal_eval(spec_str)
        return pd.Series({key: spec_dict.get(key) for key in DEFAULT_KEYS})
    except:
        return pd.Series({key: None for key in DEFAULT_KEYS})

def clean_spec_values(df):
    """
    Clean and unify inconsistent spec values (like None, '-', '16', etc.)
    """
    for col in ['display_size', 'ram', 'disk_size', 'operating_system']:
        df[col] = df[col].replace(['-', 'None', 'none', '', 'nan', 'NaN'], None)
        df[col] = df[col].fillna("Info not available")
    return df

def data_cleaning(df):
    df = df[['rating', 'reviews', 'extracted_price', 'asin', 'title', 'link_clean', 'thumbnail', 'delivery', 'scrape_date', 'specs']]

    # Step 1: Parse specs
    specs_df = df['specs'].apply(parse_specs)
    df = pd.concat([df.drop(columns=['specs']), specs_df], axis=1)

    # Step 2: Clean spec fields
    df = clean_spec_values(df)

    # Step 3: Convert to correct data types
    df = change_datatype(df)

    # Step 4: Clean delivery info
    df['delivery'] = df['delivery'].fillna('Info not available').apply(clean_delivery)

    # Step 5: Impute only numerical columns
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    imputer = SimpleImputer(strategy='mean')
    df[numerical_cols] = imputer.fit_transform(df[numerical_cols])

    # step:6 fill missing categorical columns with 'Info not available'
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    df[categorical_cols] = df[categorical_cols].fillna("Info not available")

    # step 7 : handling duplicated
    df = df.drop_duplicates(subset=["asin"], keep="first")
    
    df.to_csv('cleaned_Data.csv')
    return df


'''file merging part'''


def upsert_to_sqlite(df, db_path="laptop_prices.db", table_name="laptops"):
    df = df.copy()
    for col in df.select_dtypes(include=['datetime64[ns]']).columns:
        df[col] = df[col].dt.strftime('%Y-%m-%d')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    columns = df.columns.tolist()
    column_defs = ", ".join([
        f'"{col}" TEXT' if df[col].dtype == 'object' else
        f'"{col}" REAL' if np.issubdtype(df[col].dtype, np.number) else
        f'"{col}" TEXT'
        for col in columns
    ])
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {column_defs},
            UNIQUE(asin, scrape_date)
        );
    """)

    placeholders = ", ".join(["?"] * len(columns))
    columns_joined = ", ".join([f'"{col}"' for col in columns])
    update_clause = ", ".join([f'"{col}"=excluded."{col}"' for col in columns if col not in ['asin', 'scrape_date']])

    insert_query = f"""
        INSERT INTO {table_name} ({columns_joined})
        VALUES ({placeholders})
        ON CONFLICT(asin, scrape_date) DO UPDATE SET
        {update_clause};
    """

    cursor.executemany(insert_query, df.values.tolist())
    conn.commit()
    conn.close()


def fetch_merged_data_from_sqlite(db_path="laptop_prices.db", table_name="laptops"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


def update_merged_data(new_data_path="cleaned_Data.csv", db_path="laptop_prices.db", table_name="laptops"):
    try:
        merged_df = fetch_merged_data_from_sqlite(db_path=db_path, table_name=table_name)
    except:
        merged_df = pd.DataFrame()

    new_df = pd.read_csv(new_data_path)

    if not merged_df.empty:
        merged_df['scrape_date'] = pd.to_datetime(merged_df['scrape_date'], errors='coerce')
    new_df['scrape_date'] = pd.to_datetime(new_df['scrape_date'], errors='coerce')

    combined_df = pd.concat([merged_df, new_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=['asin', 'scrape_date'], keep='last')
    combined_df = combined_df.sort_values(by=['asin', 'scrape_date'])

    combined_df['extracted_price'] = pd.to_numeric(combined_df['extracted_price'], errors='coerce')
    combined_df['rating'] = pd.to_numeric(combined_df['rating'], errors='coerce')
    combined_df['previous_price'] = combined_df.groupby('asin')['extracted_price'].shift(1)
    combined_df['previous_scrape_date'] = combined_df.groupby('asin')['scrape_date'].shift(1)

    combined_df['price_difference'] = combined_df['extracted_price'] - combined_df['previous_price']
    combined_df['price_change_percent'] = (combined_df['price_difference'] / combined_df['previous_price']) * 100

    mask = combined_df['previous_price'].isna()
    combined_df.loc[mask, 'previous_price'] = combined_df.loc[mask, 'extracted_price']
    combined_df.loc[mask, 'price_difference'] = 0
    combined_df.loc[mask, 'price_change_percent'] = 0
    combined_df.loc[mask, 'previous_scrape_date'] = combined_df.loc[mask, 'scrape_date']

    combined_df['buy_now'] = np.where(
        (combined_df['price_change_percent'] < -5) & (combined_df['rating'] > 3.2),
        'Yes', 'No'
    )
    
    # 💡 Price stability calculation
    stability_df = combined_df.groupby('asin')['extracted_price'].std().reset_index()
    stability_df.rename(columns={'extracted_price': 'price_stability'}, inplace=True)

    # Debug print for stability_df
    print("🔍 Stability DF Preview:\n", stability_df.head())

       # Step 8: Merge price stability (left join with 'asin')
    combined_df = pd.merge(combined_df, stability_df, on='asin', how='left', suffixes=('', '_stability'))
    
    # Step 9: Handle missing price_stability
    if 'price_stability' not in combined_df.columns:
        print("⚠️ Warning: 'price_stability' column missing after merge. Filling with 0.")
        combined_df['price_stability'] = 0
    else:
        combined_df['price_stability'] = combined_df['price_stability'].fillna(0)
    
    # Step 10: Label stability
    combined_df['stability_label'] = np.where(
        combined_df['price_stability'] < 5, 'Stable', 'Unstable'
    )
    
    # Clean up: Drop any extra columns that were added accidentally (e.g., price_stability_stability)
    extra_cols = [col for col in combined_df.columns if col.endswith('_stability') and col != 'price_stability']
    combined_df.drop(columns=extra_cols, inplace=True)

    combined_df = combined_df.sort_values(by=['asin', 'scrape_date'])

    upsert_to_sqlite(combined_df, db_path=db_path, table_name=table_name)

    print("✅ Merged data updated and saved to database.")


def run_all():
    """
    Runs the full pipeline:
    1. Scrape Amazon laptop data via SerpAPI
    2. Clean and preprocess the scraped data
    3. Update SQLite database with the cleaned data
    """
    print(" Starting full pipeline...")

    # Step 1: Web Scraping
    print("\n Step 1: Web scraping started...")
    web_scraping()
    print(" Web scraping complete.")

    # Step 2: Data Cleaning
    print("\n Step 2: Cleaning data...")
    raw_df = pd.read_csv("amazon_scrape_data.csv")
    cleaned_df = data_cleaning(raw_df)
    print(f" Data cleaning complete. Saved to 'cleaned_Data.csv' ({len(cleaned_df)} rows).")

    # Step 3: Merge & Update DB
    print("\n Step 3: Updating database...")
    update_merged_data(new_data_path="cleaned_Data.csv")
    print(" Database update complete.")

    print("\n All steps completed successfully!")

    
