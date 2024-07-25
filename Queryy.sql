--- These are not all the queries I used

SELECT COUNT(*) FROM properties;

SELECT beds, COUNT(*) 
FROM properties 
GROUP BY beds 
ORDER BY COUNT(*) DESC;


SELECT * FROM properties 
WHERE location LIKE '%Sector%';

SELECT AVG(convert_price_to_millions(price)) AS avg_price_millions
FROM properties;


SELECT 
    CASE 
        WHEN convert_price_to_millions(price) < 10 THEN 'Under 10 Million'
        WHEN convert_price_to_millions(price) BETWEEN 10 AND 50 THEN '10-50 Million'
        WHEN convert_price_to_millions(price) BETWEEN 50 AND 100 THEN '50-100 Million'
        ELSE 'Over 100 Million'
    END AS price_range,
    COUNT(*) AS property_count
FROM properties
GROUP BY price_range
ORDER BY price_range;

--  Most expensive properties:
SELECT location, price, beds, area
FROM properties
ORDER BY convert_price_to_millions(price) DESC
LIMIT 10;

-- cleaning the data into table
CREATE TABLE clean_properties AS
SELECT 
    id,
    location,
    convert_price_to_millions(price) AS price_millions,
    CAST(REGEXP_REPLACE(beds, '[^0-9]', '', 'g') AS INTEGER) AS bedrooms,
    CAST(SPLIT_PART(area, ' ', 1) AS NUMERIC) AS area_marla
FROM properties;

SELECT 
    bedrooms,
    AVG(price_millions) AS avg_price_millions,
    AVG(area_marla) AS avg_area,
    COUNT(*) AS count
FROM clean_properties
GROUP BY bedrooms
ORDER BY bedrooms;