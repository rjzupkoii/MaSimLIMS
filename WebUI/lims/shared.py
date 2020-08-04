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

    
def nextPage_newRow(pageNum, rowsList):
    # If pageNum is None assume we are on the first page
    if pageNum == None: pageNum = 1

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
    # None resolves as the first page
    if pageNum == None: return 1

    # Can't navigate before the first page
    if pageNum - 1 == 0: return 1

    # Just navigage back one
    return pageNum - 1

def blankSet(rowsList):
    for row in range(0,len(rowsList)):
        for column in range(0, len(rowsList[row])):
            if not rowsList[row][column]:
                rowsList[row][column] =' '
    return rowsList


# input should be a list which contains seconds as elements
def timeAlgorithm(timeListSeconds):
    sum = 0
    for i in range(0,len(timeListSeconds)):
        sum += float(timeListSeconds[i])
    mean = round(sum/len(timeListSeconds))
    # seconds
    if mean <= 300:
        for i in range(0, len(timeListSeconds)):
            timeListSeconds[i] = round(timeListSeconds[i])
        return timeListSeconds, 'in seconds'
    elif mean <= 7200:
        timeListMinutes = []
        for i in range(0, len(timeListSeconds)):
            timeListMinutes.append(round(timeListSeconds[i]/60))
        return timeListMinutes, 'in minutes'
    else:
        timeListHours = []
        for i in range(0, len(timeListSeconds)):
            timeListHours.append(round(timeListSeconds[i]/3600,2))
        return timeListHours, 'in hours'


def manageTime(timeListSeconds,units):
    if 'seconds' in units:
        for i in range(0, len(timeListSeconds)):
            if timeListSeconds[i]:
                timeListSeconds[i] = round(timeListSeconds[i])
    elif 'minutes' in units:
        for i in range(0,len(timeListSeconds)):
            if timeListSeconds[i]:
                timeListSeconds[i] = round(timeListSeconds[i]/60)
    else:
        for i in range(0,len(timeListSeconds)):
            if timeListSeconds[i]:
                timeListSeconds[i] = round(timeListSeconds[i]/3600,2)
    return timeListSeconds