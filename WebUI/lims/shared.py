## 
# shared.py
#
# Define methods of use throughout the LIMS codebase.
##
import psycopg2
import re

# Date format
DATEFORMAT = "%Y-%m-%d %H:%M:%S"

# Define the various time attributes to be used for formatting
TIMEATTRIBUTES = { 'seconds': [1, 0], 'minutes': [60, 0], 'hours': [3600, 2] }

# Indices to use with TIMEATTRIBUTES
TIMEDIVISOR = 0
TIMEROUNDING = 1


# Select specific unit Get study name
def getStudyName(request, id = 'None'):
    # If there is not an ID, return default value
    if 'None' in id: return [["Unassigned"]]

    # Return the study name
    query = "SELECT name FROM study WHERE id = %(id)s"
    result = selectQuery(request, query, {'id':id})
    return result


# get configuration name
def getConfigName(request, id = 'None'):
    # If there is not an ID, return default value
    if 'None' in id: return [["Unassigned"]]

    # Return the configuration name
    query = "SELECT filename FROM configuration WHERE id = %(id)s"
    result = selectQuery(request, query, {'id':id})
    return result


# Need parameter input, sql syntax execution
def selectQuery(request, sql, parameter = None):
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


# Execute SQL queries that need to be committed (e.g., INSERT or DELETE) 
# parameters are assumed to prevent SQL injection
def commitQuery(request, sql, parameter, connectionString = None):
    # Open the connection
    if connectionString is None:
        connectionString = request.session['dbconnection']
    connection = psycopg2.connect(connectionString)
    cursor = connection.cursor()

    # Execute the query and commit
    cursor.execute(sql, parameter)
    connection.commit()

    # Clean-up and return
    cursor.close()
    connection.close()


# set blank space into ' '
def blankSet(rowsList):
    for row in range(0,len(rowsList)):
        for column in range(0, len(rowsList[row])):
            # If meet blank space
            if not rowsList[row][column]:
                rowsList[row][column] =' '
    return rowsList


# Update the times provided to be in the preferred unit for display and return the correct label
def timeAlgorithm(times):
    # Start by getting the mean time
    sum = 0
    for i in range(0, len(times)):
        sum += float(times[i])
    mean = round(sum / len(times))

    # Get the correct unit, default hours
    units = 'hours'

    # Return seconds if the running time is less than 5 minutes
    if mean <= 300: units = 'seconds'

    # Return minutes if running time is less than 2 hours
    elif mean <= 7200: units = 'minutes'

    # Format and return
    for i in range(0, len(times)):
        times[i] = round(times[i] / TIMEATTRIBUTES[units][TIMEDIVISOR], TIMEATTRIBUTES[units][TIMEROUNDING])
    return times, units


def manageTime(times, units):
    # Default is hours
    if units is None: units = 'hours'  
      
    # Format and return
    for i in range(0, len(times)):
        if times[i]: times[i] = round(times[i] / TIMEATTRIBUTES[units][TIMEDIVISOR], TIMEATTRIBUTES[units][TIMEROUNDING])
    return times