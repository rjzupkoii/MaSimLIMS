## 
# views.py
#
# Define the views that are used by the LIMS.
##
import psycopg2

from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from lims.shared import *

# The index of the LIMS just shows a basic list of what is running on the default database
@require_http_methods(["GET"])
def index(request):
    SQL = "SELECT id, filename, starttime, endtime, movement, runningtime " \
          "FROM (SELECT * FROM v_replicates ORDER BY starttime DESC LIMIT 100) last100 where (now()-starttime) <= interval '2 days' and endtime is null order by id desc"
    rows = selectQuery(request, SQL)

    # Render empty if there are no results
    if len(rows) == 0:
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
def replicates(request):
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


@require_http_methods(["GET"])
def setdb(request, id):
    # Validate the ID provided
    if id not in request.session['databases'].keys():
        message = "Database {} not found in registry!".format(id)
        return render(request, "empty.html", {"message": message})
    
    # Set the id and redirect to home
    request.session['database'] = id
    return redirect('/')
