import re
from pathlib import Path
import sqlite3
from flask import Flask, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "restaurants.db"

app = Flask(__name__)


def get_db_connection():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            "restaurants.db was not found. Run 'python import_data.py' first."
        )
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    search = request.args.get("q", "").strip()
    if search and not re.match(r"^[a-zA-ZæøåÆØÅ0-9\s\-']+$", search):
        search = ""
    min_rating = request.args.get("min_rating", "").strip()

    # SQL er brugt her. Vi vælger restaurants/steder i København, Danmark.
    sql = """
        SELECT
            restaurant_name,
            city,
            country,
            address,
            avg_rating,
            total_reviews_count,
            price_level,
            latitude,
            longitude
        FROM restaurants
        WHERE
            lower(country) = 'denmark'
            AND (
                lower(city) = 'copenhagen'
                OR lower(city) = 'københavn'
                OR lower(original_location) LIKE '%copenhagen%'
                OR lower(original_location) LIKE '%københavn%'
            )
    """
    params = []


    if search:
        sql += """
            AND (
                lower(restaurant_name) LIKE ?
                OR lower(address) LIKE ?
            )
        """
        like_value = f"%{search.lower()}%"
        params.extend([like_value, like_value])

    if min_rating:
        try:
            min_rating_float = float(min_rating)
            sql += " AND avg_rating >= ?"
            params.append(min_rating_float)
        except ValueError:
            # Det her gør at man ignorere invalid input så siden ikke crasher. 
            min_rating = ""

    sql += """
        ORDER BY
            avg_rating DESC,
            total_reviews_count DESC,
            restaurant_name ASC
        LIMIT 300
    """

    with get_db_connection() as conn:
        restaurants = conn.execute(sql, params).fetchall()
        total_copenhagen = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM restaurants
            WHERE lower(country) = 'denmark'
              AND (
                lower(city) = 'copenhagen'
                OR lower(city) = 'københavn'
                OR lower(original_location) LIKE '%copenhagen%'
                OR lower(original_location) LIKE '%københavn%'
              )
            """
        ).fetchone()["count"]

    return render_template(
        "index.html",
        restaurants=restaurants,
        total_copenhagen=total_copenhagen,
        search=search,
        min_rating=min_rating,
    )


@app.route("/api/copenhagen")
def api_copenhagen():
    """Small JSON endpoint, useful if you later want JavaScript or a map."""
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT restaurant_name, city, country, address, avg_rating,
                   total_reviews_count, price_level, latitude, longitude
            FROM restaurants
            WHERE lower(country) = 'denmark'
              AND (
                lower(city) = 'copenhagen'
                OR lower(city) = 'københavn'
                OR lower(original_location) LIKE '%copenhagen%'
                OR lower(original_location) LIKE '%københavn%'
              )
            ORDER BY avg_rating DESC, total_reviews_count DESC
            LIMIT 300
            """
        ).fetchall()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    app.run(debug=True)
