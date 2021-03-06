CREATE VIEW daily_status_log AS
  SELECT dt, status, COUNT(status) AS hits
    FROM (SELECT DATA (time) AS dt, status FROM log) AS sq
    GROUP BY dt, status;
