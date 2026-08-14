import os
import re
import sqlite3
import statistics
import time

import requests
import pandas as pd

from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"

GBP_TO_INR = 105.50

MIN_BOOKS_REQUIRED = 60

CATEGORY_URLS = {
    "Travel": "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
    "Mystery": "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
    "Historical Fiction": "https://books.toscrape.com/catalogue/category/books/historical-fiction_20/index.html",
    "Young Adult": "https://books.toscrape.com/catalogue/category/books/young-adult_21/index.html",
    "Science Fiction": "https://books.toscrape.com/catalogue/category/books/science-fiction_16/index.html",
}

SCRIPT_DIR = os.getcwd()
DB_PATH = os.path.join(SCRIPT_DIR, "books_catalog.db")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 20

REQUEST_DELAY = 0.15

session = requests.Session()
session.headers.update(HEADERS)

def get_soup(url):
    """
    Download a webpage and return a BeautifulSoup object.

    Raises an exception for HTTP errors.
    """

    response = session.get(
        url,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    return BeautifulSoup(
        response.text,
        "html.parser"
    )

def parse_price(price_text):
    """
    Convert price text such as:

        £51.77

    into:

        51.77

    Returns None if parsing fails.
    """

    if price_text is None:
        return None

    try:
        cleaned = (
            str(price_text)
            .replace("£", "")
            .replace("GBP", "")
            .replace(",", "")
            .strip()
        )

        match = re.search(
            r"\d+(?:\.\d+)?",
            cleaned
        )

        if not match:
            return None

        return float(match.group())

    except (ValueError, TypeError):
        return None

def parse_rating(rating_text):
    """
    Convert:

        One
        Two
        Three
        Four
        Five

    into:

        1
        2
        3
        4
        5
    """

    rating_map = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5
    }

    if rating_text is None:
        return None

    cleaned = str(rating_text).strip().lower()

    return rating_map.get(cleaned)

def parse_availability(availability_text):
    """
    Convert availability text into boolean.

    Example:

        'In stock (22 available)'

    becomes:

        True
    """

    if availability_text is None:
        return False

    return "in stock" in str(availability_text).lower()

def get_page_count(soup):
    """
    Determine how many pages exist in a category.

    The website normally has a pagination section like:

        Page 1 of 3
    """

    current_page = soup.select_one(
        ".current"
    )

    if current_page:
        text = current_page.get_text(
            " ",
            strip=True
        )

        match = re.search(
            r"Page\s+\d+\s+of\s+(\d+)",
            text,
            re.IGNORECASE
        )

        if match:
            return int(match.group(1))


    return 1

def build_page_url(first_page_url, page_number):
    """
    Convert:

        .../index.html

    to:

        .../page-2.html

        .../page-3.html

    etc.
    """

    if page_number == 1:
        return first_page_url

    base = first_page_url.rsplit(
        "/",
        1
    )[0]

    return f"{base}/page-{page_number}.html"

def scrape_category(category_name, category_url):
    """
    Scrape all books from one category.
    """

    print()
    print("=" * 70)
    print(f"SCRAPING CATEGORY: {category_name}")
    print("=" * 70)

    records = []


    try:
        soup = get_soup(category_url)

    except requests.RequestException as error:
        print(
            f"ERROR downloading category "
            f"{category_name}: {error}"
        )

        return records

    total_pages = get_page_count(soup)

    print(
        f"Pages found for {category_name}: "
        f"{total_pages}"
    )


    for page_number in range(
        1,
        total_pages + 1
    ):

        page_url = build_page_url(
            category_url,
            page_number
        )

        print(
            f"  Scraping page "
            f"{page_number}/{total_pages}..."
        )

        try:

            if page_number == 1:
                page_soup = soup
            else:
                page_soup = get_soup(
                    page_url
                )

        except requests.RequestException as error:

            print(
                f"  WARNING: Could not scrape "
                f"{page_url}: {error}"
            )

            continue


        books = page_soup.select(
            "article.product_pod"
        )

        for book in books:

            try:


                title_element = book.select_one(
                    "h3 a"
                )

                if title_element:
                    title = (
                        title_element
                        .get("title")
                        or title_element.get_text(
                            strip=True
                        )
                    )
                else:
                    title = None


                price_element = book.select_one(
                    ".price_color"
                )

                price_text = (
                    price_element.get_text(
                        strip=True
                    )
                    if price_element
                    else None
                )


                rating_element = book.select_one(
                    "p.star-rating"
                )

                if rating_element:

                    rating_classes = (
                        rating_element
                        .get("class", [])
                    )


                    rating_text = None

                    for class_name in rating_classes:

                        if class_name.lower() in {
                            "one",
                            "two",
                            "three",
                            "four",
                            "five"
                        }:
                            rating_text = class_name
                            break

                else:
                    rating_text = None


                availability_element = (
                    book.select_one(
                        ".availability"
                    )
                )

                availability_text = (
                    availability_element
                    .get_text(
                        " ",
                        strip=True
                    )
                    if availability_element
                    else None
                )


                link_element = book.select_one(
                    "h3 a"
                )

                product_url = None

                if link_element:
                    product_url = link_element.get(
                        "href"
                    )

                    if product_url:
                        product_url = (
                            BASE_URL.rstrip("/")
                            + "/catalogue/"
                            + product_url.replace(
                                "../",
                                ""
                            )
                        )


                records.append(
                    {
                        "title": title,
                        "price": price_text,
                        "star_rating": rating_text,
                        "availability": availability_text,
                        "category": category_name,
                        "product_url": product_url,
                    }
                )

            except Exception as error:


                print(
                    "  WARNING: Could not parse "
                    f"one book: {error}"
                )

                continue

        time.sleep(
            REQUEST_DELAY
        )

    print(
        f"Books scraped from "
        f"{category_name}: {len(records)}"
    )

    return records

def scrape_all_categories():

    all_records = []

    for category_name, category_url in (
        CATEGORY_URLS.items()
    ):

        category_records = scrape_category(
            category_name,
            category_url
        )

        all_records.extend(
            category_records
        )

    return all_records

def clean_data(records):

    print()
    print("=" * 70)
    print("CLEANING DATA")
    print("=" * 70)

    if not records:
        raise RuntimeError(
            "No records were scraped."
        )

    df = pd.DataFrame(records)

    print(
        f"Raw rows scraped: {len(df)}"
    )

    df = df.dropna(
        how="all"
    ).copy()

    df["title"] = (
        df["title"]
        .astype("string")
        .str.strip()
    )

    df["price_gbp"] = df[
        "price"
    ].apply(
        parse_price
    )

    df["rating"] = df[
        "star_rating"
    ].apply(
        parse_rating
    )

    df["in_stock"] = df[
        "availability"
    ].apply(
        parse_availability
    )

    df["category"] = (
        df["category"]
        .astype("string")
        .str.strip()
    )

    df = df.dropna(
        subset=[
            "title",
            "category"
        ]
    ).copy()

    numeric_columns = [
        "price_gbp",
        "rating"
    ]

    for column in numeric_columns:

        if df[column].isna().any():

            median_value = df[
                column
            ].median()

            if pd.isna(median_value):

                raise RuntimeError(
                    f"Cannot impute {column}: "
                    f"there are no valid values."
                )

            df[column] = df[
                column
            ].fillna(
                median_value
            )

            print(
                f"Median-imputed missing "
                f"{column} values with "
                f"{median_value}"
            )

    df["price_gbp"] = df[
        "price_gbp"
    ].astype(float)

    df["rating"] = df[
        "rating"
    ].astype(int)

    df["in_stock"] = df[
        "in_stock"
    ].astype(bool)

    df["price_inr"] = (
        df["price_gbp"]
        * GBP_TO_INR
    ).round(2)

    before_duplicates = len(df)

    df = df.drop_duplicates(
        subset=[
            "title",
            "category"
        ]
    ).reset_index(
        drop=True
    )

    removed_duplicates = (
        before_duplicates - len(df)
    )

    print(
        f"Duplicate rows removed: "
        f"{removed_duplicates}"
    )

    df = df[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category",
            "product_url",
            "price",
            "star_rating",
            "availability",
        ]
    ]

    print(
        f"Final cleaned rows: {len(df)}"
    )

    return df

def validate_dataset(df):

    print()
    print("=" * 70)
    print("VALIDATING DATASET")
    print("=" * 70)

    assert len(df) >= MIN_BOOKS_REQUIRED, (
        f"Dataset contains only {len(df)} rows. "
        f"At least {MIN_BOOKS_REQUIRED} are required."
    )

    category_count = (
        df["category"]
        .nunique()
    )

    assert category_count >= 3, (
        "At least 3 categories are required."
    )

    required_columns = {
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock",
        "category",
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    assert not missing_columns, (
        f"Missing required columns: "
        f"{missing_columns}"
    )

    assert not df[
        "title"
    ].isna().any()

    assert not df[
        "price_gbp"
    ].isna().any()

    assert not df[
        "price_inr"
    ].isna().any()

    assert not df[
        "rating"
    ].isna().any()

    assert not df[
        "in_stock"
    ].isna().any()

    assert not df[
        "category"
    ].isna().any()

    assert df[
        "rating"
    ].between(
        1,
        5
    ).all()

    expected_inr = (
        df["price_gbp"]
        * GBP_TO_INR
    ).round(2)

    assert (
        df["price_inr"]
        .round(2)
        .equals(
            expected_inr
        )
    )

    print(
        "✓ Minimum row requirement passed"
    )

    print(
        "✓ Minimum category requirement passed"
    )

    print(
        "✓ Required columns present"
    )

    print(
        "✓ No missing required values"
    )

    print(
        "✓ Ratings are between 1 and 5"
    )

    print(
        f"✓ GBP → INR conversion uses "
        f"fixed rate {GBP_TO_INR}"
    )

    print()
    print("DATASET VALIDATION PASSED")

def create_database():

    print()
    print("=" * 70)
    print("CREATING SQLITE DATABASE")
    print("=" * 70)

    if os.path.exists(DB_PATH):

        os.remove(
            DB_PATH
        )

        print(
            "Existing database removed."
        )

    conn = sqlite3.connect(
        DB_PATH
    )

    conn.execute(
        "PRAGMA foreign_keys = ON;"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            price_inr REAL NOT NULL,
            rating INTEGER NOT NULL,
            in_stock INTEGER NOT NULL,
            category_id INTEGER NOT NULL,

            FOREIGN KEY (
                category_id
            )
            REFERENCES categories (
                category_id
            )
        );
        """
    )

    conn.commit()

    print(
        "✓ categories table created"
    )

    print(
        "✓ books table created"
    )

    print(
        "✓ Primary key / foreign key relationship created"
    )

    return conn

def insert_data(conn, df):

    print()
    print("=" * 70)
    print("INSERTING DATA INTO SQLITE")
    print("=" * 70)

    cursor = conn.cursor()

    categories = sorted(
        df["category"]
        .dropna()
        .unique()
        .tolist()
    )

    for category in categories:

        cursor.execute(
            """
            INSERT INTO categories (
                category_name
            )
            VALUES (?);
            """,
            (category,)
        )

    conn.commit()

    category_df = pd.read_sql(
        """
        SELECT
            category_id,
            category_name
        FROM categories
        ORDER BY category_id;
        """,
        conn
    )

    category_map = dict(
        zip(
            category_df[
                "category_name"
            ],
            category_df[
                "category_id"
            ]
        )
    )

    book_rows = []

    for _, row in df.iterrows():

        book_rows.append(
            (
                str(row["title"]),
                float(row["price_gbp"]),
                float(row["price_inr"]),
                int(row["rating"]),
                int(bool(row["in_stock"])),
                int(
                    category_map[
                        row["category"]
                    ]
                ),
            )
        )

    cursor.executemany(
        """
        INSERT INTO books (
            title,
            price_gbp,
            price_inr,
            rating,
            in_stock,
            category_id
        )
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        book_rows
    )

    conn.commit()

    print(
        f"✓ Inserted {len(categories)} categories"
    )

    print(
        f"✓ Inserted {len(book_rows)} books"
    )

def show_schema(conn):

    print()
    print("=" * 70)
    print("DATABASE SCHEMA")
    print("=" * 70)

    schema = pd.read_sql(
        """
        SELECT
            name,
            type
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
        """,
        conn
    )

    print(
        schema.to_string(
            index=False
        )
    )

SQL_QUERY_1 = """
SELECT
    book_id,
    title,
    price_gbp,
    price_inr,
    rating,
    in_stock
FROM books
ORDER BY book_id
LIMIT 10;
"""

SQL_QUERY_2 = """
SELECT
    title,
    price_gbp,
    price_inr,
    rating
FROM books
WHERE rating >= 4
ORDER BY rating DESC, price_gbp ASC
LIMIT 15;
"""

SQL_QUERY_3 = """
SELECT
    title,
    price_gbp,
    price_inr,
    rating
FROM books
ORDER BY price_inr DESC
LIMIT 10;
"""

SQL_QUERY_4 = """
SELECT DISTINCT
    rating
FROM books
ORDER BY rating;
"""

SQL_QUERY_5 = """
SELECT
    title,
    rating,
    price_gbp,
    category_id
FROM books
WHERE rating IN (4, 5)
ORDER BY rating DESC, title;
"""

SQL_QUERY_6 = """
SELECT
    title,
    price_gbp,
    price_inr,
    rating
FROM books
WHERE price_gbp BETWEEN 10 AND 25
ORDER BY price_gbp;
"""

SQL_QUERY_7 = """
SELECT
    b.book_id,
    b.title,
    b.price_gbp,
    b.price_inr,
    b.rating,
    b.in_stock,
    c.category_name
FROM books AS b
INNER JOIN categories AS c
    ON b.category_id = c.category_id
ORDER BY c.category_name, b.title
LIMIT 20;
"""

SQL_QUERY_8 = """
SELECT
    c.category_name,
    COUNT(b.book_id) AS book_count,
    ROUND(AVG(b.price_gbp), 2) AS avg_price_gbp,
    ROUND(AVG(b.price_inr), 2) AS avg_price_inr,
    ROUND(AVG(b.rating), 2) AS avg_rating
FROM categories AS c
INNER JOIN books AS b
    ON c.category_id = b.category_id
GROUP BY c.category_id, c.category_name
ORDER BY book_count DESC;
"""

def run_sql_queries(conn):

    print()
    print("=" * 70)
    print("RUNNING SQL QUERIES")
    print("=" * 70)

    queries = {
        "Query 1 - SELECT": SQL_QUERY_1,
        "Query 2 - WHERE": SQL_QUERY_2,
        "Query 3 - ORDER BY + LIMIT": SQL_QUERY_3,
        "Query 4 - DISTINCT": SQL_QUERY_4,
        "Query 5 - IN": SQL_QUERY_5,
        "Query 6 - BETWEEN": SQL_QUERY_6,
        "Query 7 - JOIN": SQL_QUERY_7,
        "Query 8 - JOIN + AGGREGATION": SQL_QUERY_8,
    }

    results = {}

    for query_name, query in queries.items():

        print()
        print("-" * 70)
        print(query_name)
        print("-" * 70)

        print(query.strip())

        result = pd.read_sql(
            query,
            conn
        )

        results[
            query_name
        ] = result

        print()

        print(
            result.to_string(
                index=False
            )
        )

    return results

def demonstrate_read_sql(conn):

    print()
    print("=" * 70)
    print("PANDAS read_sql() DEMONSTRATION")
    print("=" * 70)

    df_sql_1 = pd.read_sql(
        SQL_QUERY_1,
        conn
    )

    print()
    print("DataFrame created from SQL Query 1:")
    print(
        df_sql_1.to_string(
            index=False
        )
    )

    df_sql_2 = pd.read_sql(
        SQL_QUERY_8,
        conn
    )

    print()
    print(
        "DataFrame created from SQL Query 8:"
    )

    print(
        df_sql_2.to_string(
            index=False
        )
    )

    return df_sql_1, df_sql_2

def demonstrate_pandas_merge(conn):

    print()
    print("=" * 70)
    print("PANDAS merge() DEMONSTRATION")
    print("=" * 70)

    df_books = pd.read_sql(
        """
        SELECT
            book_id,
            title,
            price_gbp,
            price_inr,
            rating,
            in_stock,
            category_id
        FROM books;
        """,
        conn
    )

    df_categories = pd.read_sql(
        """
        SELECT
            category_id,
            category_name
        FROM categories;
        """,
        conn
    )

    df_merged = pd.merge(
        df_books,
        df_categories,
        on="category_id",
        how="inner"
    )

    df_merged = df_merged[
        [
            "book_id",
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category_name",
        ]
    ].sort_values(
        [
            "category_name",
            "title"
        ]
    ).reset_index(
        drop=True
    )

    df_sql_join = pd.read_sql(
        SQL_QUERY_7,
        conn
    )

    df_sql_join = df_sql_join.sort_values(
        [
            "category_name",
            "title"
        ]
    ).reset_index(
        drop=True
    )

    df_pandas_comparison = (
        df_merged
        .head(20)
        .reset_index(drop=True)
    )

    df_sql_comparison = (
        df_sql_join
        .reset_index(drop=True)
    )

    df_pandas_comparison[
        "in_stock"
    ] = df_pandas_comparison[
        "in_stock"
    ].astype(int)

    df_sql_comparison[
        "in_stock"
    ] = df_sql_comparison[
        "in_stock"
    ].astype(int)

    equivalent = (
        df_pandas_comparison.equals(
            df_sql_comparison
        )
    )

    print()
    print(
        "SQL JOIN result:"
    )

    print(
        df_sql_comparison.to_string(
            index=False
        )
    )

    print()
    print(
        "Pandas merge() result:"
    )

    print(
        df_pandas_comparison.to_string(
            index=False
        )
    )

    print()
    print(
        f"SQL JOIN and pandas merge() "
        f"equivalent: {equivalent}"
    )

    assert equivalent, (
        "SQL JOIN and pandas merge() "
        "results are not equivalent."
    )

    print()
    print(
        "✓ SQL JOIN and pandas merge() "
        "produce equivalent output."
    )

    return (
        df_books,
        df_categories,
        df_merged
    )

def validate_database(conn):

    print()
    print("=" * 70)
    print("VALIDATING DATABASE")
    print("=" * 70)

    category_count = pd.read_sql(
        """
        SELECT COUNT(*) AS count
        FROM categories;
        """,
        conn
    ).iloc[0]["count"]

    book_count = pd.read_sql(
        """
        SELECT COUNT(*) AS count
        FROM books;
        """,
        conn
    ).iloc[0]["count"]

    print(
        f"Number of categories: "
        f"{category_count}"
    )

    print(
        f"Number of books: "
        f"{book_count}"
    )

    assert category_count >= 3
    assert book_count >= MIN_BOOKS_REQUIRED

    foreign_key_check = pd.read_sql(
        """
        PRAGMA foreign_key_check;
        """,
        conn
    )

    print(
        f"Foreign key violations: "
        f"{len(foreign_key_check)}"
    )

    assert len(
        foreign_key_check
    ) == 0

    orphan_count = pd.read_sql(
        """
        SELECT COUNT(*) AS count
        FROM books AS b
        LEFT JOIN categories AS c
            ON b.category_id = c.category_id
        WHERE c.category_id IS NULL;
        """,
        conn
    ).iloc[0]["count"]

    print(
        f"Orphaned books: "
        f"{orphan_count}"
    )

    assert orphan_count == 0

    print()
    print(
        "✓ Database validation passed."
    )

def display_final_sample(df):

    print()
    print("=" * 70)
    print("FINAL CLEANED DATASET - FIRST 20 ROWS")
    print("=" * 70)

    display_columns = [
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock",
        "category",
    ]

    print(
        df[
            display_columns
        ].head(20).to_string(
            index=False
        )
    )

    print()
    print("=" * 70)
    print("CATEGORY COUNTS")
    print("=" * 70)

    print(
        df[
            "category"
        ].value_counts().to_string()
    )

def main():

    print()
    print("=" * 70)
    print("ZEPTO CATALOG DATA ENGINEERING CAPSTONE")
    print("=" * 70)

    print()
    print(
        "Pipeline: "
        "SCRAPE -> CLEAN -> CONVERT -> STORE -> QUERY -> VALIDATE"
    )

    print()
    print(
        f"Fixed GBP -> INR rate: "
        f"{GBP_TO_INR}"
    )

    print(
        f"Required minimum books: "
        f"{MIN_BOOKS_REQUIRED}"
    )

    raw_records = scrape_all_categories()

    if len(raw_records) == 0:

        raise RuntimeError(
            "Scraping returned zero records. "
            "Check your internet connection "
            "and the source website."
        )

    print()
    print(
        f"TOTAL RAW BOOKS SCRAPED: "
        f"{len(raw_records)}"
    )

    df = clean_data(
        raw_records
    )

    validate_dataset(
        df
    )

    csv_path = os.path.join(
        SCRIPT_DIR,
        "books_cleaned.csv"
    )

    df.to_csv(
        csv_path,
        index=False
    )

    print()
    print(
        f"✓ Clean CSV saved to: "
        f"{csv_path}"
    )

    conn = create_database()

    try:

        insert_data(
            conn,
            df
        )

        validate_database(
            conn
        )

        show_schema(
            conn
        )

        sql_results = run_sql_queries(
            conn
        )

        df_sql_1, df_sql_2 = (
            demonstrate_read_sql(
                conn
            )
        )

        (
            df_books,
            df_categories,
            df_merged
        ) = demonstrate_pandas_merge(
            conn
        )

    finally:

        conn.close()

    display_final_sample(
        df
    )

    print()
    print("=" * 70)
    print("CAPSTONE PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print()
    print(
        "✓ Scraping completed"
    )

    print(
        "✓ Data cleaning completed"
    )

    print(
        "✓ Median imputation handled"
    )

    print(
        "✓ GBP → INR fixed-rate conversion completed"
    )

    print(
        "✓ SQLite normalized schema created"
    )

    print(
        "✓ Primary/foreign key relationship created"
    )

    print(
        "✓ SQL queries executed"
    )

    print(
        "✓ pandas read_sql() demonstrated"
    )

    print(
        "✓ pandas merge() demonstrated"
    )

    print(
        "✓ SQL JOIN vs pandas merge() validated"
    )

    print()
    print(
        f"Database file: {DB_PATH}"
    )

    print(
        f"CSV file: {csv_path}"
    )

    print()
    print(
        "ALL CAPSTONE REQUIREMENTS COMPLETED."
    )


if __name__ == "__main__":
    main()