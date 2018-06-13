-- 1. What are the most popular three articles of all time?
select articles.title, count(*) from articles, log where path like '%' || slug || '%' group by articles.title;

select articles.title, count(*) as hits
  from articles, log
  where path like '%' || slug || '%'
  group by articles.title
  order by hits desc
  limit 3;

-- 2.
select name, count(*) as views
  from (select name, slug from articles, authors where author = authors.id)as sq, log
  where path like '%' || sq.slug || '%'
  group by name
  order by views desc;

-- 3.
select count(dt) from (select date(time) as dt from log group by date(time)) as sq;
select dt, status, count(status) from (select date(time) as dt, status from log) as sq group by dt, status;

create view daily_status_log as
  select dt, status, count(status) as hits
    from (select date(time) as dt, status from log) as sq
    group by dt, status;

select dt, sum(case when status like '%404 NOT FOUND%' THEN hits END) / sum(hits) from daily_status_log group by dt;

select dt, error_freq
  from (select dt, sum(case when status like '%404 NOT FOUND%' THEN hits END) / sum(hits) as error_freq
          from daily_status_log group by dt) as sq
  where error_freq > 0.01;
