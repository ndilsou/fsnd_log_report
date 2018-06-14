-- 1. What are the most popular three articles of all time?
SELECT articles.title, COUNT(articles.title)
  FROM articles, log
  WHERE path LIKE '%' || slug || '%'
  GROUP BY articles.title;

SELECT articles.title, COUNT(articles.title) AS hits
  FROM articles, log
  WHERE path LIKE '%' || slug || '%'
  GROUP BY articles.title
  ORDER BY hits DESC
  limit 3;

-- 2.
SELECT name, COUNT(name) AS views
  FROM (SELECT name, slug FROM articles, authors WHERE author = authors.id) AS sq, log
  WHERE path LIKE '%' || sq.slug || '%'
  GROUP BY name
  ORDER BY views DESC;

-- 3.
CREATE VIEW daily_status_log AS
  SELECT dt, status, COUNT (status) AS hits
    FROM (SELECT DATA (time) AS dt, status FROM log) AS sq
    GROUP BY dt, status;

SELECT dt, error_freq
  FROM (FROM dt, SUM(CASE WHEN status LIKE '%404 NOT FOUND%' THEN hits END) / SUM(hits) AS error_freq
          FROM daily_status_log GROUP BY dt) AS sq
  WHERE error_freq > 0.01;
