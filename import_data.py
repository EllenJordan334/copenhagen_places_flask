"""
Import TripAdvisor European restaurants CSV into SQLite.

Put the CSV here:
    data/tripadvisor_european_restaurants.csv

Then run:
    python import_data.py
"""

from pathlib import Path
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "tripadvisor_european_restaurants.csv"
DB_PATH = BASE_DIR / "restaurants.db"
TABLE_NAME = "restaurants"

# Keep the project small and relevant for the web app.
# If some columns do not exist in your CSV, they are skipped automatically.
WANTED_COLUMNS = [
    "restaurant_name",
    "restaurant_link",
    "country",
    "region",
    "province",
    "city",
    "address",
    "original_location",
    "latitude",
    "longitude",
    "avg_rating",
    "total_reviews_count",
    "price_level",
    "price_range",
    "cuisines",
    "vegetarian_friendly",
    "vegan_options",
    "gluten_free",
]


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Make column names easier to use from SQL/Python."""
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )
    return df


def import_csv() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV file not found: {CSV_PATH}\n"
            "Download the TripAdvisor CSV and place it in data/ with this exact name:\n"
            "tripadvisor_european_restaurants.csv"
        )

    print("Reading CSV. This can take a little while because the dataset is large...")
    df = pd.read_csv(CSV_PATH, encoding="utf-8", low_memory=False)
    df = normalize_column_names(df)

    existing_columns = [col for col in WANTED_COLUMNS if col in df.columns]
    df = df[existing_columns]

    # Make filtering safer by replacing missing city/country values with empty strings.
    for col in ["city", "country", "restaurant_name"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    # Optional: remove exact duplicate restaurant links if the column exists.
    if "restaurant_link" in df.columns:
        df = df.drop_duplicates(subset=["restaurant_link"])

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

        # Indexes make the Copenhagen search faster.
        conn.execute("CREATE INDEX IF NOT EXISTS idx_restaurants_city ON restaurants(city)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_restaurants_country ON restaurants(country)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_restaurants_name ON restaurants(restaurant_name)")

    print(f"Done. Imported {len(df):,} rows into {DB_PATH}")
    print("You can now run: flask --app app run --debug")


if __name__ == "__main__":
    import_csv()
