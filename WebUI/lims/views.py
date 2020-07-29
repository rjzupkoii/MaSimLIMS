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
    # Get the data for the view
    rows = AppDatabase.getReplicates(request, True)

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
    return render(request, 'replicate.html', {"rows": newRow,"newPathPart":'', "pageNumberPrev":str(pageNumberPrev), "pageNumberNext":str(pageNumberNext),"viewType": "Currently running for"})


# This view will render the last 100 replicates that ran on the database
@api_view(["POST","GET"])
def replicatesLatest100(request):
    # Get the data for the view
    rows = AppDatabase.getReplicates(request, False, 100)

    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        # start time
        rowsList[ndx][2] = rowsList[ndx][2].strftime(DATEFORMAT)
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime(DATEFORMAT)

    ReplicateID = []
    runningTimeListFinished = []
    runningTimeListUnfinished = []
    runningTimeListWorth = []
    for i in range(0, len(rowsList)):
        # The database provides running time, format it as a string
        rowsList[i][-1] = str(rowsList[i][-1])

        ReplicateID.append(rowsList[i][0])
        runningTime = 0
        
        # If we have an end time, finished
        if rowsList[i][3]:
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

    # Return the results based upon how we were called
    if request.method == "POST":
        return JsonResponse({'rowsList': rowsList, 'runningTimeListWorth': runningTimeListWorth, 'runningTimeListFinished': runningTimeListFinished, 
            'runningTimeListUnfinished': runningTimeListUnfinished, 'ReplicateID': ReplicateID})
    elif request.method == "GET":
        return render(request, 'last100.html', {"rows": rowsList,"viewType": "Last 100 replicates on","localURL":'/replicatesLatest100'})
    # error case
    else:
        # This shouldn't happen so allow an exception handler to catch it
        raise ValueError("{}, request.method is not either \"GET\" or \"POST\"".format(replicatesLatest100.__name__,))


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
@api_view(["GET","POST"])
def study(request):
    # Get the data for the view
    rows = AppDatabase.getStudies(request)
    
    #Page Number cannot be smaller than 1
    # pageNumberPrev = pagePrev(pageNum)
    # pageNumberNext, newRow = nextPage_newRow(pageNum,rows)
    # newPathPart = pathReformateNoLast(request.path)
    if request.method == "POST":
        return JsonResponse({'rowsList': rows})
    elif request.method == "GET":
        return render(request, 'index.html',{"rows": rows, "viewType": "Studies on","localURL":"/study"})


# Configurations that associate with study id
@api_view(["GET","POST"])
def StudyConfig(request,id):
    # newPathPart = pathReformateNoLast(request.path)
    #Page Number cannot be smaller than 1
    # pageNumberPrev = pagePrev(pageNum)
    # If study id is None
    if "None" in id:
        rows = AppDatabase.getStudyConfigurations(request)
    # If study ID is a number
    else:
        # Fetch from table
        rows = AppDatabase.getStudyConfigurations(request,id)
        # Based on study id -> get study name
    studyname = getStudyName(request, id)
    # pageNumberNext, newRow = nextPage_newRow(pageNum,rows)
    if request.method == "POST":
        return JsonResponse({'rowsList': rows})
    elif request.method == "GET":
        return render(request,"Config.html",{"rows":rows,"viewType": "Configurations on Study: \""+studyname[0][0]+'\" - ',"localURL":'/StudyConfig/'+str(id)})


# Replicates that associate with study id
@api_view(["GET", "POST"])
def StudyReplicate(request, id):
    # newPathPart = pathReformateNoLast(request.path)
    #Page Number cannot be smaller than 1
    # pageNumberPrev = pagePrev(pageNum)
    if "None" in id:
        rows = AppDatabase.getStudyReplicates(request)
    else:
        rows = AppDatabase.getStudyReplicates(request,id)
        # Based on study id -> get study name
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][1] = rowsList[ndx][1].strftime(DATEFORMAT)
        # Only when endtime and runningtime exist, we process the data
        if rowsList[ndx][2]:
            rowsList[ndx][2] = rowsList[ndx][2].strftime(DATEFORMAT)
        rowsList[ndx][-1] = str(rowsList[ndx][-1])
    studyname = getStudyName(request, id)
    # pageNumberNext, newRow = nextPage_newRow(pageNum,rowsList)
    if request.method == "POST":
        return JsonResponse({'rowsList': rowsList})
    elif request.method == "GET":
        return render(request, 'replicate.html', {"rows": rowsList,"viewType": "Replicates on Study: \""+studyname[0][0]+'\" - ',"localURL":'/StudyReplicate/'+str(id)})


# Insert data into study table
@api_view(["POST"])
def setStudyInsert(request):
    try:
        name = request.POST["studyName"]
        if len(name) < 1:
            messages.success(request, "Please input at least one character!")
        else:
            AppDatabase.insertStudy(request, name)
    except (Exception,psycopg2.DatabaseError) as error:
        messages.success(request, error)
    return redirect('/study/1')

# Need more details, when we delete study, do we need to delete study notes also?????
# Delete data from study table
@api_view(["DELETE"])
def DeleteFail(request, id):
    # Note two queries being run in same transaction
    SQL = """DELETE FROM notes WHERE studyid = %(id)s;
             DELETE FROM study WHERE id = %(id)s"""
    commitQuery(request,SQL,{'id':id})
    return HttpResponse("OK")


# Replicates that associate with configuration id
@api_view(["GET","POST"])
def ConfigReplicate(request, id):
    # newPathPart = pathReformateNoLast(request.path)
    #Page Number cannot be smaller than 1
    # pageNumberPrev = pagePrev(pageNum)
    # If NULL
    if "None" in id:
        rows = AppDatabase.getConfigReplicate(request)
    # If a number is received
    else:
        rows = AppDatabase.getConfigReplicate(request,id)
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][1] = rowsList[ndx][1].strftime(DATEFORMAT)
        # Only when endtime and runningtime exist, we process the data
        if rowsList[ndx][2]:
            rowsList[ndx][2] = rowsList[ndx][2].strftime(DATEFORMAT)
        rowsList[ndx][-1] = str(rowsList[ndx][-1])
    configurationName = getConfigName(request, id)
    # Get next page number and new row value
    # pageNumberNext, newRow = nextPage_newRow(pageNum,rowsList)
    if request.method == "POST":
        return JsonResponse({'rowsList': rowsList})
    elif request.method == "GET":
        return render(request, 'Replicate.html', {"rows": rowsList, "viewType": "Replicates on Configuration: \""+configurationName[0][0]+"\" - ","localURL":'/ConfigReplicate/'+str(id)})


# Not within latest 100 and interval > 2 days and not end. (Data that worth to notice) --> may add parameter in the future
@api_view(["GET","POST"])
def worthToNotice(request):
    # Get the data for the view
    rows  = AppDatabase.getLongRunningReplicates(request)

    # Return if we have no records
    if len(rows) == 0:
        message = "{0}, no replicates needs to be noticed".format(request.session['dbname'])
        return render(request, "empty.html", {"message": message})

    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][1] = rowsList[ndx][1].strftime(DATEFORMAT)
        # The database provides running time, format it as a string
        rowsList[ndx][-1] = str(rowsList[ndx][-1])

    # #Page Number cannot be smaller than 1
    # pageNumberPrev = pagePrev(pageNum)
    # pageNumberNext, newRow = nextPage_newRow(pageNum,rowsList)
    # newPathPart = pathReformateNoLast(request.path)
    if request.method == "POST":
        return JsonResponse({'rowsList':rowsList})
    elif request.method == "GET":
        return render(request, 'Replicate.html', {"rows": rowsList, "viewType": "Long Running Replicates on", "localURL":'/worthToNotice'})


@api_view(["GET"])
# id is study id
def studyNotes(request,studyId,pageNum):
    newPathPart = pathReformateNoLast(request.path)
    #Page Number cannot be smaller than 1
    pageNumberPrev = pagePrev(pageNum)
    rows = AppDatabase.getStudyNotes(request,studyId)
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
    AppDatabase.insertNotes(request,notes,user,studyId)
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
    AppDatabase.deleteNotes(request, id)
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