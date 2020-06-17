## 
# views.py
#
# Define the views that are used by the LIMS.
##

import psycopg2

from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from lims.shared import *

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
        rowsList[ndx][2] = rowsList[ndx][2].strftime("%m/%d/%Y, %H:%M:%S")
        rowsList[ndx][3] = rowsList[ndx][3]
        rowsList[ndx][5] = rowsList[ndx][5]
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
        rowsList[ndx][2] = rowsList[ndx][2].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[ndx][5]:
            rowsList[ndx][5] = int(rowsList[ndx][5].total_seconds() * 1000000)
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
    # This query has problem
    SQL = "select s.id, s.name, count(c.id) configs, count(r.id) replicates from study s left join configuration c on c.studyid = s.id left join v_replicates r on r.configurationid = c.id group by s.id"\
    " union SELECT studyid, CASE WHEN name IS NULL THEN 'Unassigned' ELSE name END, configs, replicates FROM" \
    " (SELECT s.id, studyid, s.name, COUNT(c.id) configs, COUNT(r.id) replicates"\
    " FROM sim.configuration c LEFT JOIN sim.replicate r ON r.configurationid = c.id LEFT JOIN sim.study s ON s.id = c.studyid GROUP BY s.id, studyid, s.name) iq order by id "
    rows = selectQuery(request,SQL)
    return render(request, 'index.html',{"rows": rows, "viewType": "Studies on"})

# Configurations that associate with study id
@require_http_methods(["GET"])
def StudyConfig(request,id):
    # If study id is None
    if "None" in id:
        SQL="select configuration.id, configuration.name, configuration.notes, configuration.filename, concat('(', ncols, ', ', nrows, ', ', xllcorner, ', ', yllcorner, ', ', cellsize, ')') as spatial, count(replicate.id) from configuration left join replicate on replicate.configurationid = configuration.id where studyid is NULL group by configuration.id order by configuration.id"
        rows = selectQuery(request,SQL)
    # If study ID is a number
    else:
        SQL = "select configuration.id, configuration.name, configuration.notes, configuration.filename, concat('(', ncols, ', ', nrows, ', ', xllcorner, ', ', yllcorner, ', ', cellsize, ')') as spatial, count(replicate.id) " \
              "from configuration left join replicate on replicate.configurationid = configuration.id where studyid = %(id)s group by configuration.id order by configuration.id"
        # Fetch from table
        rows = selectQueryParameter(request,SQL,{'id':id})
    return render(request,"Config.html",{"rows":rows, "viewType": "Configurations on"})

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
        rows = selectQueryParameter(request, SQL,{'id':id})
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][2] = rowsList[ndx][2].strftime("%m/%d/%Y, %H:%M:%S")
        # Only when endtime and runningtime exist, we process the data
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[ndx][5]:
            rowsList[ndx][5] = int(rowsList[ndx][5].total_seconds() * 1000000)
    return render(request, 'replicate.html', {"rows": rowsList, "viewType": "Replicates on"})

# Insert data into study table
@require_http_methods(["GET"])
def setStudyInsert(request):
    # Examine the name first
    # When the user clicks "Submit" the form should check to see if a name was entered (i.e., more than 1 character), if it is valid then it is submitted to the server.
    try:
        name = request.GET["studyName"]
        # This works but need real database
        if len(name) < 1:
            messages.success(request, "Please input at least one character!")
        else:
            SQL = "select id from study"
            rows = selectQuery(request,SQL)
            # Get current database's current last ID
            lastID = rows[-1][0]
            # Do not reuse the primary key
            # sql: """SELECT admin FROM users WHERE username = %(username)s"""
            # parameter: {'username': username}
            SQL = """insert into study values (%(id)s, %(name)s)"""
            commitQuery(request,SQL, {'id':str(lastID+1), 'name':name})
    except (Exception,psycopg2.DatabaseError) as error:
        messages.success(request, error)
    return redirect('/study')

# Delete data from study table
@require_http_methods(["GET"])
def DeleteFail(request, id):
    SQL = """delete from study where id = %(id)s"""
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
        rows = selectQueryParameter(request,SQL, {'id':id})
    rowsList = []
    for ndx in range(0, len(rows)):
        rowsList.append(list(rows[ndx]))
        rowsList[ndx][2] = rowsList[ndx][2].strftime("%m/%d/%Y, %H:%M:%S")
        # Only when endtime and runningtime exist, we process the data
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[ndx][5]:
            rowsList[ndx][5] = int(rowsList[ndx][5].total_seconds() * 1000000)
    return render(request, 'replicate.html', {"rows": rowsList, "viewType": "Replicates on"})

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
        rowsList[ndx][2] = rowsList[ndx][2].strftime("%m/%d/%Y, %H:%M:%S")
        # Only when endtime and runningtime exist, we process the data
        if rowsList[ndx][3]:
            rowsList[ndx][3] = rowsList[ndx][3].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[ndx][5]:
            rowsList[ndx][5] = int(rowsList[ndx][5].total_seconds() * 1000000)
    return render(request, 'replicate.html', {"rows": rowsList, "viewType": "Long Running Replicates on"})