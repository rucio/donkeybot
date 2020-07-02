# Sqlite Wrapper

To be able to cache the data between each stage in the bot's creation and use we need to have consistent communication with a database. Since for our use case there was no need for more advanced databases like MongoDB or other relational database, we simply create .db files with sqlite to hold our data.

To help us with this and provide methods that utilize sqlite we made `database.py`, that basically is an sqlite wrapper. It includes both general methods like `query(self, query_string)` and `create_table(self, table_name, columns)` but also more custom methods like `insert_email(self, email_obj, table_name)` and `insert_question(self, question_obj, table_name)` which are specific for our case.

The attributes of `Database` class are the following:
| Column            | Description                           |   
| :----             | :-----------                          |
| db_name           | database's name (`db_name.db`)        |
| db                | database connection object            |
| default_table     | the default table (usually `emails`)  |
| cursor            | cursor object of the database         |

Additional attributes exist only in circumstance. For example if the `get_tables(self)` method is called we also now have the `self.tables` attribute. Or when `create_table(self, table_name, columns)` is called then `self.cols` holds the column info for the newly created table.