## 
# shared.py
#
# Define methods of use throughout the LIMS codebase.
##
# I keep debug rows
import psycopg2

# No parameter
def selectQuery(request, sql):
    # Open the connection
    connection = psycopg2.connect(request.session['dbconnection'])
    cursor = connection.cursor()
    # Execute the query, note the rows
    cursor.execute(sql)
    print('selectQuery')
    print(cursor.query.decode('utf-8'))
    rows = cursor.fetchall()

    # Clean-up and return
    cursor.close()
    connection.close()
    return rows
# Need parameter input
def selectQueryParameter(request, sql, parameter):
    # Open the connection
    connection = psycopg2.connect(request.session['dbconnection'])
    cursor = connection.cursor()
    # Execute the query, note the rows
    cursor.execute(sql, parameter)
    print('selectQueryParameter')
    print(cursor.query.decode('utf-8'))
    rows = cursor.fetchall()

    # Clean-up and return
    cursor.close()
    connection.close()
    return rows
# Some SQL syntaxs need to be commited. i.e. insertion and delete
# cursor.execute("""SELECT admin FROM users WHERE username = %(username)s""", {'username': username})
# sql: """SELECT admin FROM users WHERE username = %(username)s"""
# parameter: {'username': username}
# modern database adapters, come with built-in tools for preventing Python SQL injection by using query parameters.
def commitQuery(request, sql, parameter):
    # Open the connection
    connection = psycopg2.connect(request.session['dbconnection'])
    cursor = connection.cursor()
    # Execute the query, note the rows
    cursor.execute(sql, parameter)
    print('commitQuery')
    print(cursor.query.decode('utf-8'))
    # commit the changes
    connection.commit()

    # Clean-up and return
    cursor.close()
    connection.close()
    return