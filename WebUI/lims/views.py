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
@api_view(["GET","POST"])
def index(request):
    # Get the data for the view
    rows = AppDatabase.getReplicates(request, True)

    # Render empty if there are no results
    if len(rows) == 0:
        # Get the dbname
        message = "{0}, no replicates running".format(request.session['dbname'])
        return render(request, "empty.html", {"message": message})

    # Render the rows        
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][1] = rowsList[ndx][1].strftime(DATEFORMAT)
        rowsList[ndx][-1] = str(rowsList[ndx][-1])
    # Let's keep this feature for now, I will find a better way to solve this.
    # if not pageNum:
    #     return redirect('/1')
    if request.method == "POST":
        return JsonResponse({'rowsList': rowsList})
    elif request.method == "GET":
        # pageNumberNext, newRow = nextPage_newRow(pageNum,rowsList)
        return render(request, 'Replicate.html', {"rows": rowsList,"viewType": "Currently running for", "localURL":'/'})


# This view will render the last 100 replicates that ran on the database
@api_view(["POST","GET"])
def replicatesLatest100(request):
    # Get the data for the view
    timeWorth = 2*24*3600
    rows = AppDatabase.getReplicates(request, False, 100)
    ReplicateID = []
    runningTimeListFinished = []
    runningTimeListUnfinished = []
    runningTimeListWorth = []
    filesName = []
    last100Time = []
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        # start time
        rowsList[ndx][2] = rowsList[ndx][2].strftime(DATEFORMAT)
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime(DATEFORMAT)

    for i in range(0, len(rowsList)):
        filesName.append(rowsList[i][1])
        # The database provides running time, format it as a string
        rowsList[i][-1] = str(rowsList[i][-1])

        ReplicateID.append(i+1)
        runningTime = 0
        # If we have an end time, finished
        # when finished --> unfinished and worthtonotice are None
        if rowsList[i][3]:
            # Days need to be fixed
            runningTime = rows[i][-1].total_seconds()
            runningTimeListFinished.append(runningTime)
            runningTimeListUnfinished.append(None)
            runningTimeListWorth.append(None)
        # If the data is still running
        # some of them are worth to notice
        # running time = current time - start time
        else:
            runningTime = (datetime.strptime(datetime.now().strftime(DATEFORMAT),DATEFORMAT) - datetime.strptime(rowsList[i][2],DATEFORMAT)).total_seconds()
            runningTimeListFinished.append(None)
            if runningTime >= timeWorth:
                runningTimeListUnfinished.append(None)
                runningTimeListWorth.append(runningTime)
            else:
                runningTimeListUnfinished.append(runningTime)
                runningTimeListWorth.append(None)
        last100Time.append(runningTime)
    rowsList = blankSet(rowsList)
    # Return the results based upon how we were called
    if request.method == "POST":
        runningTimeListWorth.reverse()
        runningTimeListFinished.reverse()
        runningTimeListUnfinished.reverse()
        filesName.reverse()
        last100Time.reverse()

        last100Time, units = timeAlgorithm(last100Time)
        runningTimeListWorth = manageTime(runningTimeListWorth,units)
        runningTimeListFinished = manageTime(runningTimeListFinished, units)
        runningTimeListUnfinished = manageTime(runningTimeListUnfinished,units)
        
        # ReplicateID.reverse()
        return JsonResponse({'rowsList': rowsList, 'runningTimeListWorth': runningTimeListWorth, 'runningTimeListFinished': runningTimeListFinished, 
            'runningTimeListUnfinished': runningTimeListUnfinished, 'ReplicateID': ReplicateID,'filesName':filesName,'last100Time':last100Time,'units':units})
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
    return redirect('/')


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
    rowsList = blankSet(rowsList)
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
    return redirect('/study')


# Delete data from study table
@api_view(["DELETE"])
def DeleteFail(request, id):
    # Note two queries being run in same transaction
    AppDatabase.deleteStudy(request,id)
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
    rowsList = blankSet(rowsList)
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
        rowsList[ndx][-2] = str(rowsList[ndx][-2])
        rowsList[ndx].append(rows[ndx][-2].total_seconds())
    if request.method == "POST":
        return JsonResponse({'rowsList':rowsList})
    elif request.method == "GET":
        return render(request, 'longRunningReplicate.html', {"rows": rowsList, "viewType": "Long Running Replicates on", "localURL":'/worthToNotice'})


@api_view(["DELETE"])
# Used for delete long running replicates (individualy)
def deleteLongRunning(request,replicateID):
    app = AppDatabase()
    # Return a boolean
    success = app.deleteReplicate(request,replicateID)
    return JsonResponse({"success":success})



@api_view(["GET","POST"])
# id is study id
def studyNotes(request,studyId):
    # newPathPart = pathReformateNoLast(request.path)
    #Page Number cannot be smaller than 1
    # pageNumberPrev = pagePrev(pageNum)
    rows = AppDatabase.getStudyNotes(request,studyId)
    rowsList = []
    # id,data, user, date,studyid
    # data, user, date, studyid,id
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        # Only when endtime and runningtime exist, we process the data
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime(DATEFORMAT)
        tmp = rowsList[ndx].pop(0)
        rowsList[ndx].append(tmp)
    tableNeed = len(rowsList) != 0
    # If 'username' is cookies, we get cookie
    if 'username' in request.COOKIES:
        user = getcookie(request,'username')
    # If not, make it empty
    else:
        user = ""
    studyName = getStudyName(request, studyId)
    # pageNumberNext, newRow = nextPage_newRow(pageNum,rowsList)
    rowsList = blankSet(rowsList)
    if request.method == "POST":
        return JsonResponse({'rowsList':rowsList})
    elif request.method == "GET":
        return render(request, 'notes.html', {"rows":rowsList, "tableNeed":tableNeed,
                            "id": studyId, "user":user, "studyName":studyName[0][0],"viewType":"Notes on Study: \""+studyName[0][0]+"\" - ","localURL":'/Study/Notes/'+str(studyId)})


# statistics only for finished
@api_view(["GET","POST"])
def studyChart(request,studyId):
    timeWorth = 2*24*3600
    rows = AppDatabase.getStudyReplicates(request,studyId)
    runningTimeListFinished = []
    runningTimeListUnfinished = []
    runningTimeListWorth = []
    filesName = []
    units = []
    allRunningTime = []
    ReplicateID = []
    rowsList = []
    finishedCount = 0
    #  v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][1] = rowsList[ndx][1].strftime(DATEFORMAT)
        # Only when endtime and runningtime exist, we process the data
        if rowsList[ndx][2]:
            rowsList[ndx][2] = rowsList[ndx][2].strftime(DATEFORMAT)
        rowsList[ndx][-1] = str(rowsList[ndx][-1])

    for i in range(0, len(rowsList)):
        ReplicateID.append(i+1)
        filesName.append(rowsList[i][0])
        runningTime = 0
        runningTimeDay = 0
        # If we have an end time, finished
        # when finished --> unfinished and worthtonotice are None
        if rowsList[i][2]:
            finishedCount += 1
            # Split running time
            runningTimeTmp = rowsList[i][-1].split(':')
            # If finished and needs several days.
            if 'day' in runningTimeTmp[0]:
                # How many days
                runningTimeDay = float(runningTimeTmp[0].split(' ')[0])
                runningTime = float(runningTimeDay*24*3600) + float(runningTimeTmp[0].split(' ')[-1])*3600 + float(runningTimeTmp[1])*60+ float(runningTimeTmp[2])
            # No more than one day.
            else:
                runningTime = float(runningTimeTmp[0])*3600 + float(runningTimeTmp[1])*60+ float(runningTimeTmp[2])
            runningTimeListFinished.append(runningTime)
            runningTimeListUnfinished.append(None)
            runningTimeListWorth.append(None)

        # If the data is still running
        # some of them are worth to notice
        # running time = current time - start time
        else:
            runningTime = (datetime.strptime(datetime.now().strftime(DATEFORMAT),DATEFORMAT) - datetime.strptime(rowsList[i][1],DATEFORMAT)).total_seconds()
            runningTimeListFinished.append(None)
            # If worth to notice, no need to mark as unfinished
            if runningTime >= timeWorth:
                runningTimeListUnfinished.append(None)
                runningTimeListWorth.append(runningTime)
            else:
                runningTimeListWorth.append(None)
                runningTimeListUnfinished.append(runningTime)
        # allRunningTime includes all running time
        allRunningTime.append(runningTime)
    rowsList = blankSet(rowsList)
    studyname = getStudyName(request, studyId)[0][0]
    if request.method == "POST":
        runningTimeListWorth.reverse()
        runningTimeListFinished.reverse()
        runningTimeListUnfinished.reverse()
        filesName.reverse()
        allRunningTime.reverse()
        allRunningTime, units = timeAlgorithm(allRunningTime)
        runningTimeListWorth = manageTime(runningTimeListWorth,units)
        runningTimeListFinished = manageTime(runningTimeListFinished, units)
        runningTimeListUnfinished = manageTime(runningTimeListUnfinished,units) 
        return JsonResponse({'rowsList': rowsList, 'runningTimeListWorth': runningTimeListWorth, 'runningTimeListFinished': runningTimeListFinished, 
            'runningTimeListUnfinished': runningTimeListUnfinished,'filesName':filesName,'allRunningTime':allRunningTime,'units':units,"ReplicateID":ReplicateID,"studyname":studyname,"finishedCount":finishedCount})
    elif request.method == "GET":
        allRunningTime, units = timeAlgorithm(allRunningTime)
        return render(request, 'studyChart.html', {"rows": rowsList,"viewType": "Replicates chart on study: ",'allRunningTime':allRunningTime,'units':units,"studyname":studyname,"localURL":'/Study/Chart/'+str(studyId)})


# id is study id
@api_view(["POST"])
def studyNotesRecord(request,studyId):
    notes = request.POST["notes"]
    user = request.POST["UserName"]
    # user is reserved in postgresql, so use "user" to avoid this.
    AppDatabase.insertNotes(request,notes,user,studyId)
    path = "/Study/Notes/" + studyId
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
    return redirect('/')