DROP TABLE IF EXISTS PopularBusinesses, SuccessfulBusinesses CASCADE;

CREATE TABLE IF NOT EXISTS PopularBusinesses AS
WITH RankedCheckins AS (
    SELECT 
        b.business_id,
        b.name,
        c.category_name,
        b.numCheckins,
        PERCENT_RANK() OVER (
            PARTITION BY c.category_name
            ORDER BY b.numCheckins DESC
        ) AS percentile
    FROM Business b
    JOIN Categories c ON b.business_id = c.business_id
),
TopCheckins AS (
    SELECT business_id
    FROM RankedCheckins
    WHERE percentile <= 0.15
), 
RankedReviews AS (
    SELECT
        b.business_id,
        b.name,
        c.category_name,
        b.review_count,
        PERCENT_RANK() OVER (
            PARTITION BY c.category_name
            ORDER BY b.review_count DESC
        ) AS percentile
        FROM business b
        JOIN Categories c ON b.business_id = c.business_id
), 
TopReviews AS (
    SELECT business_id
    FROM RankedReviews
    WHERE percentile <= 0.15
)
SELECT DISTINCT b.business_id, b.name
FROM Business b
JOIN TopCheckins tc ON b.business_id = tc.business_id
JOIN TopReviews tr ON b.business_id = tr.business_id;

CREATE TABLE IF NOT EXISTS SuccessfulBusinesses AS
SELECT business_id, name, reviewrating, review_count
FROM Business
Where reviewrating >= 3.5 AND review_count >= 200;