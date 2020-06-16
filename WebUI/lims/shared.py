## 
# shared.py
#
# Define methods of use throughout the LIMS codebase.
##
import psycopg2

def selectQuery(request, sql):
    # Open the connection
    connection = psycopg2.connect(request.session['dbconnection'])
    cursor = connection.cursor()

    # Execute the query, note the rows
    cursor.execute(sql)
    rows = cursor.fetchall()

    # Clean-up and return
    cursor.close()
    connection.close()
    return rows
# Some SQL syntaxs need to be commited. i.e. insertion and delete
def commitQuery(request, sql):
    # Open the connection
    connection = psycopg2.connect(request.session['dbconnection'])
    cursor = connection.cursor()
    # Execute the query, note the rows
    cursor.execute(sql)
    # commit the changes
    connection.commit()

    # Clean-up and return
    cursor.close()
    connection.close()
    return