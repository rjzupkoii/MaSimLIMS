## 
# views.py
#
# Define the views that are used by the LIMS.
##

import psycopg2
import os
from django.http import JsonResponse
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view
from datetime import datetime
from lims.shared import *
from lims.AppDatabase import *


def error_404_view(request, exception):
    return render(request,'404.html')


# The index of the LIMS just shows a basic list of what is running on the default database
@api_view(["GET"])
def index(request, pageNum = None):
    SQL = "SELECT id, filename, starttime, endtime, movement, runningtime " \
          "FROM (SELECT * FROM v_replicates ORDER BY starttime DESC LIMIT 100) last100 where (now()-starttime) <= interval '2 days' and endtime is null order by id desc"
    rows = selectQuery(request, SQL)
    # Render empty if there are no results
    if len(rows) == 0:
        # Get the dbname
        message = "{0}, no replicates running".format(request.session['dbname'])
        return render(request, "empty.html", {"message": message})
    #Page Number cannot be smaller than 1
    pageNumberPrev = pagePrev(pageNum)
    # Render the rows        
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][2] = rowsList[ndx][2].strftime(DATEFORMAT)
    # Let's keep this feature for now, I will find a better way to solve this.
    if not pageNum:
        return redirect('/1')
    pageNumberNext, newRow = nextPage_newRow(pageNum,rowsList)
    newPathPart = ''
    return render(request, 'replicate.html', {"rows": newRow,"newPathPart":newPathPart, "pageNumberPrev":str(pageNumberPrev), "pageNumberNext":str(pageNumberNext),"viewType": "Currently running for"})

# This view will render the last 100 replicates that ran on the database
@api_view(["POST","GET"])
def replicatesLatest100(request):
    SQL = "select * from (SELECT id, filename, starttime, endtime, movement, runningtime " \
        "FROM v_replicates ORDER BY starttime DESC LIMIT 100) as output order by id DESC"
    rows = selectQuery(request, SQL)
    rowsList = []
    runningTimeListFinished = []
    runningTimeListUnfinished = []
    runningTimeListWorth = []
    ReplicateID = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        # start time
        rowsList[ndx][2] = rowsList[ndx][2].strftime(DATEFORMAT)
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime(DATEFORMAT)
    for i in range(0, len(rowsList)):
        ReplicateID.append(rowsList[i][0])
        runningTime = 0
        # If we have running time, finished
        if rowsList[i][-1]:
            rowsList[i][-1] = str(rowsList[i][-1])
            runningTimeTmp = rowsList[i][-1].split(':')
            runningTime = float(runningTimeTmp[0])*3600 + float(runningTimeTmp[1])*60+ float(runningTimeTmp[2])
            runningTimeListFinished.append(runningTime)
            runningTimeListUnfinished.append(None)
        # If the data is still running
        # running time = current time - start time
        else:
            runningTime = (datetime.strptime(datetime.now().strftime(DATEFORMAT),DATEFORMAT) - datetime.strptime(rowsList[i][2],DATEFORMAT)).total_seconds()
            runningTimeListUnfinished.append(runningTime)
            runningTimeListFinished.append(None)
        if runningTime >= 2*24*3600:
            runningTimeListWorth.append(runningTime)
        else:
            runningTimeListWorth.append(None)
    if request.method == "POST":
        return JsonResponse({'rowsList': rowsList,'runningTimeListWorth':runningTimeListWorth,'runningTimeListFinished':runningTimeListFinished,'runningTimeListUnfinished':runningTimeListUnfinished,
                            'ReplicateID':ReplicateID})
    # add else or change into else 
    elif request.method == "GET":
        return render(request, 'last100.html', {"rows": rowsList,"viewType": "Last 100 replicates on"})
    # error case
    else:
        message = "{0}, request.method is not either \"GET\" or \"POST\"".format(request.session['dbname'])
        return render(request, "empty.html", {"message": message})


# setup connection "session"
@api_view(["GET"])
def setdb(request, id):
    # Validate the ID provided
    if id not in request.session['databases'].keys():
        message = "Database {} not found in registry!".format(id)
        return render(request, "empty.html", {"message": message})
    
    # Set the id and redirect to home
    request.session['database'] = id
    return redirect('/1')


# Show study table
@api_view(["GET"])
def study(request,pageNum):
    newPathPart = pathReformateNoLast(request.path)
    #Page Number cannot be smaller than 1
    pageNumberPrev = pagePrev(pageNum)
    SQL = """
    SELECT s.id, s.name, COUNT(DISTINCT c.id) configs, COUNT(DISTINCT r.id) replicates 
    FROM sim.study s 
      LEFT JOIN sim.configuration c ON c.studyid = s.id 
      LEFT JOIN v_replicates r on r.configurationid = c.id 
    GROUP BY s.id
    UNION
    SELECT studyid, 
      CASE WHEN name IS NULL THEN 'Unassigned' ELSE name END, configs, replicates 
    FROM
    (SELECT s.id, studyid, s.name, COUNT(DISTINCT c.id) configs, COUNT(DISTINCT r.id) replicates
     FROM sim.configuration c 
       LEFT JOIN sim.replicate r ON r.configurationid = c.id 
       LEFT JOIN sim.study s ON s.id = c.studyid 
     GROUP BY s.id, studyid, s.name) iq order by id"""
    rows = selectQuery(request,SQL)
    pageNumberNext, newRow = nextPage_newRow(pageNum,rows)
    return render(request, 'index.html',{"rows": newRow, "newPathPart":newPathPart, "pageNumberPrev":str(pageNumberPrev), "pageNumberNext":str(pageNumberNext), "viewType": "Studies on"})


# Configurations that associate with study id
@api_view(["GET"])
def StudyConfig(request,id,pageNum):
    newPathPart = pathReformateNoLast(request.path)
    #Page Number cannot be smaller than 1
    pageNumberPrev = pagePrev(pageNum)
    # If study id is None
    if "None" in id:
        SQL="select configuration.id, configuration.name, configuration.notes, configuration.filename, concat('(', ncols, ', ', nrows, ', ', xllcorner, ', ', yllcorner, ', ', cellsize, ')') as spatial, count(replicate.id) from configuration left join replicate on replicate.configurationid = configuration.id where studyid is NULL group by configuration.id order by configuration.id"
        rows = selectQuery(request, SQL)
    # If study ID is a number
    else:
        SQL = "select configuration.id, configuration.name, configuration.notes, configuration.filename, concat('(', ncols, ', ', nrows, ', ', xllcorner, ', ', yllcorner, ', ', cellsize, ')') as spatial, count(replicate.id) " \
              "from configuration left join replicate on replicate.configurationid = configuration.id where studyid = %(id)s group by configuration.id order by configuration.id"
        # Fetch from table
        rows = selectQuery(request, SQL, {'id':id})
        # Based on study id -> get study name
    studyname = getStudyName(request, id)
    pageNumberNext, newRow = nextPage_newRow(pageNum,rows)
    return render(request,"Config.html",{"rows":newRow, "newPathPart":newPathPart, "pageNumberPrev":str(pageNumberPrev), "pageNumberNext":str(pageNumberNext),"viewType": "Configurations on Study: \""+studyname[0][0]+'\" - '})


# Replicates that associate with study id
@api_view(["GET"])
def StudyReplicate(request, id,pageNum):
    newPathPart = pathReformateNoLast(request.path)
    #Page Number cannot be smaller than 1
    pageNumberPrev = pagePrev(pageNum)
    if "None" in id:
        SQL = "select v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime " \
              "from configuration inner join v_replicates on v_replicates.configurationid = configuration.id where studyid is NULL order by v_replicates.id"
        rows = selectQuery(request,SQL)
    else:
        SQL = "select v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime from study left join configuration on configuration.studyID = "\
            "%(id)s inner join v_replicates on v_replicates.configurationid = configuration.id where study.id = %(id)s order by v_replicates.id"
        rows = selectQuery(request, SQL,{'id':id})
        # Based on study id -> get study name
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][2] = rowsList[ndx][2].strftime(DATEFORMAT)
        # Only when endtime and runningtime exist, we process the data
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime(DATEFORMAT)
    studyname = getStudyName(request, id)
    pageNumberNext, newRow = nextPage_newRow(pageNum,rowsList)
    return render(request, 'replicate.html', {"rows": newRow, "newPathPart":newPathPart, "pageNumberPrev":str(pageNumberPrev), "pageNumberNext":str(pageNumberNext),"viewType": "Replicates on Study: \""+studyname[0][0]+'\" - '})


# Insert data into study table
@api_view(["POST"])
def setStudyInsert(request):
    try:
        name = request.POST["studyName"]
        if len(name) < 1:
            messages.success(request, "Please input at least one character!")
        else:
            SQL = 'INSERT INTO study (name) VALUES (%(name)s)'
            commitQuery(request, SQL, {'name':name})
    except (Exception,psycopg2.DatabaseError) as error:
        messages.success(request, error)
    return redirect('/study/1')


# Delete data from study table
@api_view(["DELETE"])
def DeleteFail(request, id):
    # Note two queries being run in same transaction
    SQL = """DELETE FROM notes WHERE studyid = %(id)s;
             DELETE FROM study WHERE id = %(id)s"""
    commitQuery(request,SQL,{'id':id})
    return HttpResponse("OK")


# Replicates that associate with configuration id
@api_view(["GET"])
def ConfigReplicate(request, id,pageNum):
    newPathPart = pathReformateNoLast(request.path)
    #Page Number cannot be smaller than 1
    pageNumberPrev = pagePrev(pageNum)
    # If NULL
    if "None" in id:
        SQL = "select v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime " \
              "from v_replicates where configurationid is NULL order by v_replicates.id"
        rows = selectQuery(request,SQL)
    # If a number is received
    else:
        SQL = "select v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime " \
              "from v_replicates where configurationid = %(id)s order by v_replicates.id"
        rows = selectQuery(request,SQL, {'id': id})
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][2] = rowsList[ndx][2].strftime(DATEFORMAT)
        # Only when endtime and runningtime exist, we process the data
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime(DATEFORMAT)
    configurationName = getConfigName(request, id)
    # Get next page number and new row value
    pageNumberNext, newRow = nextPage_newRow(pageNum,rowsList)
    return render(request, 'replicate.html', {"rows": newRow, "newPathPart":newPathPart, "pageNumberPrev":str(pageNumberPrev), 
        "pageNumberNext":str(pageNumberNext), "viewType": "Replicates on Configuration: \""+configurationName[0][0]+"\" - "})


# Not within latest 100 and interval > 2 days and not end. (Data that worth to notice) --> may add parameter in the future
@api_view(["GET"])
def worthToNotice(request,pageNum):
    newPathPart = pathReformateNoLast(request.path)
    #Page Number cannot be smaller than 1
    pageNumberPrev = pagePrev(pageNum)
    # Not within latest 100 and interval > 2 days and not end
    SQL = "select id, filename, starttime, endtime, movement, runningtime from v_replicates " \
          "where starttime < (SELECT min(starttime) FROM (SELECT starttime FROM v_replicates ORDER BY starttime DESC LIMIT 100) last100) " \
          "and (now()-starttime) > interval '2 days' and endtime is null order by id desc"
    rows = selectQuery(request, SQL)
    if len(rows) == 0:
        # Get the dbname
        message = "{0}, no replicates needs to be noticed".format(request.session['dbname'])
        return render(request, "empty.html", {"message": message})
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][2] = rowsList[ndx][2].strftime(DATEFORMAT)
        # Only when endtime and runningtime exist, we process the data
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime(DATEFORMAT)
    pageNumberNext, newRow = nextPage_newRow(pageNum,rowsList)
    return render(request, 'replicate.html', {"rows": newRow, "newPathPart":newPathPart, "pageNumberPrev":str(pageNumberPrev), 
        "pageNumberNext":str(pageNumberNext),"viewType": "Long Running Replicates on"})


@api_view(["GET"])
# id is study id
def studyNotes(request,studyId,pageNum):
    newPathPart = pathReformateNoLast(request.path)
    #Page Number cannot be smaller than 1
    pageNumberPrev = pagePrev(pageNum)
    SQL = "SELECT * from notes where studyid = %(id)s order by date desc"
    rows = selectQuery(request, SQL,{"id":studyId})
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        # Only when endtime and runningtime exist, we process the data
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime(DATEFORMAT)
    tableNeed = len(rowsList) != 0
    # If 'username' is cookies, we get cookie
    if 'username' in request.COOKIES:
        user = getcookie(request,'username')
    # If not, make it empty
    else:
        user = ""
    studyName = getStudyName(request, studyId)
    pageNumberNext, newRow = nextPage_newRow(pageNum,rowsList)
    return render(request, 'notes.html', {"rows":newRow, "tableNeed":tableNeed,"newPathPart":newPathPart, "pageNumberPrev":str(pageNumberPrev), 
        "pageNumberNext":str(pageNumberNext),"id": studyId,"user":user, "studyName":studyName[0][0],"viewType":"Notes on Study: \""+studyName[0][0]+"\" - "})


# id is study id
@api_view(["POST"])
def studyNotesRecord(request,studyId):
    notes = request.POST["notes"]
    user = request.POST["UserName"]
    # user is reserved in postgresql, so use "user" to avoid this.
    SQL = """insert into notes (data, "user", date, studyid) values (%(data)s,%(user)s,now(),%(studyid)s)"""
    commitQuery(request,SQL, {'data':notes, 'user': user, 'studyid':studyId})
    path = "/Study/Notes/" + studyId+'/1'
    # set cookies and connect cookies with response
    response = redirect(path)
    # cookie is for global
    setcookie(response,'username',user)
    return response


@api_view(["DELETE"])
#Study/DeleteNotes/<str: studyid>/<str:id>
# first parameter is studyid, the second one is id of notes
def DeleteNotes(request, studyId, id):
    SQL = """delete from notes where id = %(id)s"""
    commitQuery(request,SQL, {"id":id})
    return HttpResponse("OK")


@api_view(["GET"])
def createNewDatabase(request):
    return render(request,'createDatabase.html',{"viewType":"Creating Database"})


# This view creates a new database using the database administrator username and 
# password supplied, regardless of operation success, the user receives a status
# message in the same database they are in. 
@api_view(["POST"])
def createDatabase(request):
    # Get the information from the request
    username = request.POST['userName']
    password = request.POST['Password']
    database = request.POST['databaseName']

    # Database name should be checked for compliance with SQL lexicon before the operation takes place
    if not re.search("^[A-Za-z_][A-Za-z\d_]{0,31}$",database):
        messages.success(request, "Please input an database name that satisfies requirements: 1 to 31 characters and start with letter or underscore may contain letters, numbers, or underscores after that")
        return redirect("/createNewDatabase")
        
    # Clone the database and respond to errors
    try:
        app = AppDatabase()
        app.cloneDatabase(request,username, password, database)
    except (Exception,psycopg2.DatabaseError) as error:
        messages.success(request, error)
        return redirect("/createNewDatabase")
    return redirect('/1')