#!/usr/bin/env python

from __future__ import print_function
import datetime
from contextlib import contextmanager
import argparse

import bleach
import psycopg2 as dbdriver


@contextmanager
def session():
    """
    Adds support for with statement to create and close a session.
    """

    db = dbdriver.connect("dbname=news")
    try:
        yield db
    finally:
        db.close()


def create_daily_status_log_view():
    """
    Creates a view in the news database to support the generation of this
    report.
    Will display an error message if the view already exists.
    :return: None
    """

    query = """
CREATE VIEW daily_status_log AS
  (SELECT dt, status, COUNT(status) AS hits
    FROM (SELECT  DATE(time) AS dt, status FROM log) AS sq
    GROUP BY dt, status);

    """

    print("adding daily_status_log view to news database...")
    with session() as sess:
        c = sess.cursor()
        try:
            c.execute(query)
        except dbdriver.ProgrammingError as e:
            print("Error: ", e)
    print("done.")


def fetch_most_popular_articles(n):
    """
    queries the news database for the n most popular articles in term of page
    viewed.
    :param n: <int> number of articles to return.
    :return: <list[tuple[str, int]]> Sorted list of records containing the
    article name and views count.
    """

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
    """
    queries the news database for the most popular authors.
    :return: <list[tuple[str, int]]> Sorted list of records containing the
    author name and views count.
    """

    query = """
SELECT name, COUNT(name) AS views
  FROM (SELECT name, slug FROM articles, authors WHERE author = authors.id) 
    AS sq, log
  WHERE path LIKE '%' || sq.slug || '%'
  GROUP BY name
  ORDER BY views DESC;"""

    with session() as sess:
        c = sess.cursor()
        c.execute(query)
        records = c.fetchall()

    return records


def fetch_error_summary(cutoff):
    """
    queries the news database for the days with and error rate superior
    to the cutoff.
    :param cutoff: <float> minimum error rate for a day to be reported.
    :return: <list[tuple[str, int]]> Sorted list of records containing
    the day in format ISO and error rate.
    """

    query = """
SELECT dt, error_freq
  FROM (SELECT dt, SUM(CASE 
                        WHEN status LIKE '%%404 NOT FOUND%%' 
                        THEN hits END) / SUM(hits) 
            AS error_freq
          FROM daily_status_log GROUP BY dt) AS sq
  WHERE error_freq > %(pct)s;

    """

    with session() as sess:
        c = sess.cursor()
        c.execute(query, {"pct": cutoff})
        records = c.fetchall()

    return records


def break_line(size):
    """
    Utility to add a line break to the displayed report.
    :param size: length of the line break.
    :return: None
    """

    print("=" * size)


def popular_articles_view(n_articles):
    """
    Displays the n most popular articles and their view count
    to standard output.
    :param n_articles: <int> number of articles to report.
    :return: None
    """

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
    """
    Display the authors, with their popularity in terms of views, to standard
    output.
    :return: None
    """

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
    """
    Display the dates with an error rate higher than the cutoff to standard
    output
    :param pct_cutoff: <float> minimum error rate for a day to be displayed.
    :return: None
    """

    msg = "days did more than {pct:.2%} of requests lead to errors"\
        .format(pct=pct_cutoff)
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
    """
    Displays the news database report.
    :param n_articles: <int> minimum error rate for a day to be displayed.
    :param pct_cutoff: <float> number of articles to report.
    :return: None
    """

    print("NEWS DATABASE REPORT ({})\n".format(datetime.datetime.now()))
    popular_articles_view(n_articles)
    authors_view()
    error_summary_view(pct_cutoff)
    print("DONE.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser("LogReport",
                                     description="A Simple information summary "
                                                 "for the news database.")
    parser.add_argument("--n", dest="n_articles",
                        help="Set the number of articles displayed in report.",
                        default=3)
    parser.add_argument("--p", dest="pct_cutoff",
                        help="Percent used as cutoff for error reporting.",
                        type=float, default=0.01)
    parser.add_argument("-create_views", dest="is_creating_view",
                        help="Creates the supporting views in the database.",
                        action='store_true')

    args = parser.parse_args()
    if args.is_creating_view:
        create_daily_status_log_view()
    else:
        n_articles = args.n_articles
        pct_cutoff = args.pct_cutoff
        main(n_articles, pct_cutoff)
