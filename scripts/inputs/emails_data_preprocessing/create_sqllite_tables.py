import sqlite3
from sqlite3 import Error
sqlitedb = './db/emails.db'

# creating db
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        return conn
    except Error as e:
        print(e)
    
    return None


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def main():

    sql_create_emails_table = """ CREATE TABLE IF NOT EXISTS emails (
                                        sender text,
                                        receiver text,
                                        subject text,
                                        date text,
                                        thread text,
                                        body text
                                    ); """


    # create a database connection
    conn = create_connection(sqlitedb)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_emails_table)

    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
