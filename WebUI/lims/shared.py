## 
# shared.py
#
# Define methods of use throughout the LIMS codebase.
##
import psycopg2
import re

DATEFORMAT = "%Y-%m-%d %H:%M:%S"
# Select specific unit
def getStudyName(request, id = 'None'):
    # If there is not an ID, return default value
    if 'None' in id:
        return [["Unassigned"]]

    # Return the study name
    query = "SELECT name FROM study WHERE id = %(id)s"
    result = selectQuery(request, query, {'id':id})
    return result

def getConfigName(request, id = 'None'):
    # If there is not an ID, return default value
    if 'None' in id:
        return [["Unassigned"]]
    # Return the configuration name
    query = "SELECT filename FROM configuration WHERE id = %(id)s"
    result = selectQuery(request, query, {'id':id})
    return result

# Get the cookie based upon the name
def getcookie(request, cookieName):  
    cookie  = request.COOKIES[cookieName]
    return cookie 


# Need parameter input
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


# Set the cookie
def setcookie(response, cookieName, value):    
    response.set_cookie(cookieName, value)
    return response  


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
    return


def visitor_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def pathReformateNoLast(pathPrepare):
    pathPrepare = pathPrepare.split('/')
    newPathPart = ""
    # Now we have new path
    for i in range(1,len(pathPrepare)-1):
        newPathPart += '/'
        newPathPart += pathPrepare[i]
    return newPathPart

    
def nextPage_newRow(pageNum,rowsList):
    newRow = []
    # if nextPage is 1, we can move to the next page, else stop moving
    nextPage = 1
    for i in range((pageNum-1)*20,pageNum*20):
        # this means that we reach the last element of the table, next page is empty and no need to show
        if i == len(rowsList)-1:
            nextPage = 0
        if i >= len(rowsList):
            nextPage = 0
            break
        newRow.append(rowsList[i])
    if nextPage:
        pageNumberNext = pageNum + 1
    else:
        pageNumberNext = pageNum
    return pageNumberNext, newRow
def pagePrev(pageNum):
    if pageNum - 1 == 0:
        pageNumberPrev = 1
    else:
        pageNumberPrev = pageNum - 1
    return pageNumberPrev