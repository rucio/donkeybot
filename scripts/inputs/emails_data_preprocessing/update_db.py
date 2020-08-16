import sqlite3
from sqlite3 import Error

sqlitedb = "./db/emails.db"


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def _add_row(conn, row):
    """
    Create a new project into the projects table
    :param conn:     connection to db
    :param table:    TODO
    :param row:      array of values, be careful about order. 
    :return: id
    """
    sql = """ INSERT INTO emails(sender, receiver, subject, date, thread, body)
              VALUES(?,?,?,?,?,?) """
    cur = conn.cursor()
    cur.execute(sql, row)
    return cur.lastrowid


def add_row(row):

    # create a database connection
    conn = create_connection(sqlitedb)
    with conn:
        _add_row(conn, row)
