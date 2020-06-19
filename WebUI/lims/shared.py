## 
# shared.py
#
# Define methods of use throughout the LIMS codebase.
##

import psycopg2

# Select query with no parameter
def selectQuery(request, sql):
    return selectQueryParameter(request, sql, None)


# Select query with parameters
def selectQueryParameter(request, sql, parameter):
    # Open the connection
    connection = psycopg2.connect(request.session['dbconnection'])
    cursor = connection.cursor()

    # Execute the query, note the rows
    if parameter is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, parameter)
    rows = cursor.fetchall()

    # Clean-up and return
    cursor.close()
    connection.close()
    return rows


# Perform an SQL operation that requires a commit
def commitQuery(request, sql, parameter):
    # Open the connection
    connection = psycopg2.connect(request.session['dbconnection'])
    cursor = connection.cursor()

    # Execute the query and commit
    cursor.execute(sql, parameter)
    connection.commit()

    # Clean-up and return
    cursor.close()
    connection.close()