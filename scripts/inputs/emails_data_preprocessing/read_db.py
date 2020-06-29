import sqlite3
from sqlite3 import Error
sqlitedb = './db/emails.db'

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def select_all_emails(conn):
    """
    Query all rows in the emails table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM emails")

    rows = cur.fetchall()

    return rows


def select_emails_by_sender(conn, sender):
    """
    Query emails by sender
    :param conn: the Connection object
    :param sender:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM emails WHERE sender=?", (sender,))

    rows = cur.fetchall()

    for row in rows:
        print(row)


def main():

    # create a database connection
    conn = create_connection(sqlitedb)
    with conn:
        for email in list(select_all_emails(conn)):
            print(email[1])


if __name__ == '__main__':
    main()
