import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def enterdata(connectionURL):
    conn = sqlite3.connect(connectionURL)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS login_details (username text, password text);")
    c.execute('insert into login_details values ("SuperUser", "SuperUser")')
    c.execute('insert into login_details values ("Manager1", "Manager1Password")')
    c.execute('insert into login_details values ("Manager2", "Manager2Password")')
    c.execute('insert into login_details values ("Employee1", "Password1")')
    c.execute('insert into login_details values ("Employee2", "Password2")')
    c.execute('insert into login_details values ("Employee3", "Password3")')
    conn.commit()
    conn.close()

# def enterDataIntoEmployees():
#     conn = sqlite3.connect('employees.sqlite3')
#     c = conn.cursor()
#     c.execute("CREATE TABLE IF NOT EXISTS employees (employee_id INTEGER NOT NULL, username VARCHAR(100), name VARCHAR(100),	designation VARCHAR(100), salary FLOAT, address VARCHAR(100), 'pNumber' VARCHAR(50), manager VARCHAR(200), password VARCHAR(200), age VARCHAR(10), PRIMARY KEY (employee_id));")
#     # c.execute('insert into login_details values ("SuperUser", "SuperUser")')
#     # c.execute('insert into login_details values ("Manager1", "Manager1Password")')
#     # c.execute('insert into login_details values ("Manager2", "Manager2Password")')
#     # c.execute('insert into login_details values ("Employee1", "Password1")')
#     # c.execute('insert into login_details values ("Employee2", "Password2")')
#     # c.execute('insert into login_details values ("Employee3", "Password3")')
#     conn.commit()
#     conn.close()


if __name__ == '__main__':
    enterdata()
    # create_connection(r"login_details.sqlite3")
    # enterdata(r"login_details.sqlite3")
