## 
# views.py
#
# Define the views that are used by the LIMS.
##

import psycopg2
import os

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from lims.shared import *
from lims.AppDatabase import *

# TODO Move this to a better location for settings
DATEFORMAT = "%Y-%m-%d %H:%M:%S"
def error_404_view(request, exception):
    return render(request,'404.html')

# The index of the LIMS just shows a basic list of what is running on the default database
@require_http_methods(["GET"])
def index(request):
    SQL = "SELECT id, filename, starttime, endtime, movement, runningtime " \
          "FROM (SELECT * FROM v_replicates ORDER BY starttime DESC LIMIT 100) last100 where (now()-starttime) <= interval '2 days' and endtime is null order by id desc"
    rows = selectQuery(request, SQL)

    # Render empty if there are no results
    if len(rows) == 0:
        # Get the dbname
        message = "{0}, no replicates running".format(request.session['dbname'])
        return render(request, "empty.html", {"message": message})

    # Render the rows        
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][2] = rowsList[ndx][2].strftime(DATEFORMAT)
    return render(request, 'replicate.html', {"rows": rowsList, "viewType": "Currently running for"})


# This view will render the last 100 replicates that ran on the database
@require_http_methods(["GET"])
def replicatesLatest100(request):
    SQL = "SELECT id, filename, starttime, endtime, movement, runningtime " \
          "FROM v_replicates ORDER BY starttime DESC LIMIT 100"
    rows = selectQuery(request, SQL)
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][2] = rowsList[ndx][2].strftime(DATEFORMAT)
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime(DATEFORMAT)
    return render(request, 'replicate.html', {"rows": rowsList, "viewType": "Last 100 replicates on"})


# setup connection "session"
@require_http_methods(["GET"])
def setdb(request, id):
    # Validate the ID provided
    if id not in request.session['databases'].keys():
        message = "Database {} not found in registry!".format(id)
        return render(request, "empty.html", {"message": message})
    
    # Set the id and redirect to home
    request.session['database'] = id
    return redirect('/')


# Show study table
@require_http_methods(["GET"])
def study(request):
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
    return render(request, 'index.html',{"rows": rows, "viewType": "Studies on"})


# Configurations that associate with study id
@require_http_methods(["GET"])
def StudyConfig(request,id):
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
    return render(request,"Config.html",{"rows":rows, "viewType": "Configurations on Study: \""+studyname[0][0]+'\" - '})


# Replicates that associate with study id
@require_http_methods(["GET"])
def StudyReplicate(request, id):
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
    return render(request, 'replicate.html', {"rows": rowsList, "viewType": "Replicates on Study: \""+studyname[0][0]+'\" - '})


# Insert data into study table
@require_http_methods(["POST"])
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
    return redirect('/study')


# Delete data from study table
@require_http_methods(["GET"])
def DeleteFail(request, id):
    # Note two queries being run in same transaction
    SQL = """DELETE FROM notes WHERE studyid = %(id)s;
             DELETE FROM study WHERE id = %(id)s"""
    commitQuery(request,SQL,{'id':id})
    return redirect('/study')


# Replicates that associate with configuration id
@require_http_methods(["GET"])
def ConfigReplicate(request, id):
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
    configurationName = getStudyName(request, id)
    return render(request, 'replicate.html', {"rows": rowsList, "viewType": "Replicates on Configuration: \""+configurationName[0][0]+"\" - "})


# Not within latest 100 and interval > 2 days and not end. (Data that worth to notice) --> may add parameter in the future
@require_http_methods(["GET"])
def worthToNotice(request):
    # Not within latest 100 and interval > 2 days and not end
    SQL = "select id, filename, starttime, endtime, movement, runningtime from v_replicates " \
          "where starttime < (SELECT min(starttime) FROM (SELECT starttime FROM v_replicates ORDER BY starttime DESC LIMIT 100) last100) " \
          "and (now()-starttime) > interval '2 days' and endtime is null order by id desc"
    rows = selectQuery(request, SQL)
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][2] = rowsList[ndx][2].strftime(DATEFORMAT)
        # Only when endtime and runningtime exist, we process the data
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime(DATEFORMAT)
    return render(request, 'replicate.html', {"rows": rowsList, "viewType": "Long Running Replicates on"})


@require_http_methods(["GET"])
# id is study id
def studyNotes(request,studyId):
    print(visitor_ip_address(request))
    SQL = "SELECT * from notes where studyid = %(id)s order by date desc"
    rows = selectQuery(request, SQL,{"id":studyId})
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        # Only when endtime and runningtime exist, we process the data
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime(DATEFORMAT)
    # If 'username' is cookies, we get cookie
    if 'username' in request.COOKIES:
        user = getcookie(request,'username')
    # If not, make it empty
    else:
        user = ""
    studyName = getStudyName(request, studyId)
    return render(request, 'notes.html', {"rows":rowsList,"id": studyId,"user":user, "studyName":studyName[0][0],"viewType":"Notes on Study: \""+studyName[0][0]+"\" - "})


# id is study id
@require_http_methods(["POST"])
def studyNotesRecord(request,studyId):
    notes = request.POST["notes"]
    user = request.POST["UserName"]
    # user is reserved in postgresql, so use "user" to avoid this.
    SQL = """insert into notes (data, "user", date, studyid) values (%(data)s,%(user)s,now(),%(studyid)s)"""
    commitQuery(request,SQL, {'data':notes, 'user': user, 'studyid':studyId})
    path = "/Study/Notes/" + studyId
    # set cookies and connect cookies with response
    response = redirect(path)
    # cookie is for global
    setcookie(response,'username',user)
    return response


@require_http_methods(["GET"])
#Study/DeleteNotes/<str: studyid>/<str:id>
# first parameter is studyid, the second one is id of notes
def DeleteNotes(request, studyId, id):
    SQL = """delete from notes where id = %(id)s"""
    rows = commitQuery(request,SQL, {"id":id})
    path = "/Study/Notes/" + studyId
    return redirect(path);
    

# This view creates a new database using the database administrator username and 
# password supplied, regardless of operation success, the user receives a status
# message in the same database they are in. 
@require_http_methods(["POST"])
def createDatabase(request):

    # Prepare the connection string
    username = ''    # TODO get the username from the form
    password = ''    # TODO Get password from the form
    
    # Prepare the query
    database = ''    # TODO Get database from form    
    
    # Prepare an updated connection string
    app = AppDatabase()
    app.cloneDatabase(username, password, database)

    # TODO Return something more informative than this
    return HttpResponse('Called, success')