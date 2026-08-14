-- ============================================================
-- ZEPTO CATALOG CAPSTONE - SQL QUERIES
-- ============================================================


-- ============================================================
-- QUERY 1: SELECT + LIMIT
-- ============================================================

SELECT
    book_id,
    title,
    price_gbp,
    price_inr,
    rating,
    in_stock
FROM books
LIMIT 10;


-- ============================================================
-- QUERY 2: WHERE
-- ============================================================

SELECT
    title,
    price_gbp,
    price_inr,
    rating
FROM books
WHERE rating >= 4
ORDER BY rating DESC;


-- ============================================================
-- QUERY 3: ORDER BY + LIMIT
-- ============================================================

SELECT
    title,
    price_gbp,
    price_inr,
    rating
FROM books
ORDER BY price_inr DESC
LIMIT 10;


-- ============================================================
-- QUERY 4: DISTINCT
-- ============================================================

SELECT DISTINCT
    rating
FROM books
ORDER BY rating;


-- ============================================================
-- QUERY 5: IN
-- ============================================================

SELECT
    title,
    rating,
    price_gbp
FROM books
WHERE rating IN (4, 5)
ORDER BY rating DESC;


-- ============================================================
-- QUERY 6: BETWEEN
-- ============================================================

SELECT
    title,
    price_gbp,
    price_inr,
    rating
FROM books
WHERE price_gbp BETWEEN 10 AND 25
ORDER BY price_gbp;


-- ============================================================
-- QUERY 7: JOIN
-- ============================================================

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


-- ============================================================
-- QUERY 8: JOIN + GROUP BY + AGGREGATION
-- ============================================================

SELECT
    c.category_name,
    COUNT(b.book_id) AS book_count,
    ROUND(AVG(b.price_gbp), 2) AS avg_price_gbp,
    ROUND(AVG(b.price_inr), 2) AS avg_price_inr,
    ROUND(AVG(b.rating), 2) AS avg_rating
FROM categories AS c
INNER JOIN books AS b
    ON c.category_id = b.category_id
GROUP BY
    c.category_id,
    c.category_name
ORDER BY book_count DESC;