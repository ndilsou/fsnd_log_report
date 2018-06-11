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
