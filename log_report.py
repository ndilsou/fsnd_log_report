#!/usr/bin/python

from __future__ import print_function
import datetime
from contextlib import contextmanager
import argparse

import bleach
import psycopg2 as dbdriver


@contextmanager
def session():
    db = dbdriver.connect("dbname=news")
    try:
        yield db
    finally:
        db.close()


def fetch_most_popular_articles(n):
    query = """
    SELECT articles.title, COUNT(articles.title) AS hits
      FROM articles, log
      WHERE path LIKE '%%' || slug || '%%'
      GROUP BY articles.title
      ORDER BY hits DESC
      limit %s;"""

    with session() as sess:
        c = sess.cursor()
        c.execute(query, (n,))
        records = c.fetchall()

    return records


def fetch_authors_by_popularity():
    query = """
SELECT name, COUNT(name) AS views
  FROM (SELECT name, slug FROM articles, authors WHERE author = authors.id) AS sq, log
  WHERE path LIKE '%' || sq.slug || '%'
  GROUP BY name
  ORDER BY views DESC;"""

    with session() as sess:
        c = sess.cursor()
        c.execute(query)
        records = c.fetchall()

    return records


def fetch_error_summary(cutoff):
    query = """
SELECT dt, error_freq
  FROM (SELECT dt, SUM(CASE WHEN status LIKE '%%404 NOT FOUND%%' THEN hits END) / SUM(hits) AS error_freq
          FROM daily_status_log GROUP BY dt) AS sq
  WHERE error_freq > %(pct)s;

    """

    with session() as sess:
        c = sess.cursor()
        c.execute(query, {"pct": cutoff})
        records = c.fetchall()

    return records


def break_line(size):
    print("=" * size)


def popular_articles_view(n_articles):
    msg = "most {n} popular articles of all time".format(n=n_articles)
    print(msg)
    break_line(len(msg))
    try:
        records = fetch_most_popular_articles(n_articles)
        for record in records:
            print("\"{}\" -- {} views".format(*record))
    except Exception as e:
        print("Error: ", e)

    print()


def authors_view():
    msg = "most popular article authors of all time"
    print(msg)
    break_line(len(msg))
    try:
        records = fetch_authors_by_popularity()
        for record in records:
            print("{} - {} views".format(*record))
    except Exception as e:
        print("Error: ", e)

    print()


def error_summary_view(pct_cutoff):
    msg = "days did more than {pct:.0%} of requests lead to errors".format(pct=pct_cutoff)
    print(msg)
    break_line(len(msg))
    try:
        records = fetch_error_summary(pct_cutoff)
        for record in records:
            print("{} - {:.2%} errors".format(*record))
    except Exception as e:
        print("Error: ", e)

    print()


def main(n_articles, pct_cutoff):
    print("NEWS DATABASE REPORT ({})\n".format(datetime.datetime.now()))
    popular_articles_view(n_articles)
    authors_view()
    error_summary_view(pct_cutoff)
    print("DONE.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", dest="n_articles", help="Set the number of articles displayed in report.", default=3)
    parser.add_argument("--p", dest="pct_cutoff", help="Percent used as cutoff for error reporting.", default=0.01)
    args = parser.parse_args()
    n_articles = args.n_articles
    pct_cutoff = args.pct_cutoff
    main(n_articles, pct_cutoff)
