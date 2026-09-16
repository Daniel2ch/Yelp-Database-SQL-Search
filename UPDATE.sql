UPDATE Business
SET numCheckins = temp.total_checkins
FROM (
    SELECT business_id, SUM(count) AS total_checkins
    FROM Checkin
    GROUP BY business_id
)   AS temp
WHERE Business.business_id = temp.business_id;

UPDATE Business
SET review_count = temp.review_total
FROM (
	SELECT business_id, COUNT(*) AS review_total
	FROM Review
	GROUP BY business_id
) AS temp
WHERE Business.business_id = temp.business_id;

UPDATE Business
SET reviewrating = temp.avg_rating
FROM (
    SELECT business_id, AVG(stars) AS avg_rating
    FROM Review
    GROUP BY business_id
)   AS temp
WHERE Business.business_id = temp.business_id;

UPDATE Users
SET review_count = temp.review_total
FROM (
    SELECT user_id, COUNT(*) AS review_total
    FROM Review
    GROUP BY user_id
) AS temp
WHERE Users.user_id = temp.user_id;

UPDATE Users
SET average_stars = temp.avg_stars
FROM (
    SELECT user_id, AVG(stars) AS avg_stars
    FROM Review
    GROUP BY user_id
) AS temp
WHERE Users.user_id = temp.user_id;