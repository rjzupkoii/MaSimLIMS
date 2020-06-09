from django.shortcuts import render
import psycopg2
# Create your views here.
def latestMasim(request):
    # within first 100, start within two days, and endtime is Null.
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="masim",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    sql = "SELECT v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime FROM v_replicates ORDER BY starttime DESC LIMIT 100"
    cur.execute(sql)
    rows = cur.fetchall()
    rowsList = []
    for i in range(0, len(rows)):
        rowsList.append(list(rows[i]))
    for i in range(0, len(rowsList)):
        rowsList[i][2] = rowsList[i][2].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[i][3]:
            rowsList[i][3] = rowsList[i][3].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[i][5]:
            rowsList[i][5] = int(rowsList[i][5].total_seconds() * 1000000)
    cur.close()
    con.close()
    return render(request, 'Replicate.html', {"rows": rowsList})
def latestBurkinaFaso(request):
    # within first 100, start within two days, and endtime is Null.
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="burkinafaso",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    sql = "SELECT v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime FROM v_replicates ORDER BY starttime DESC LIMIT 100"
    cur.execute(sql)
    rows = cur.fetchall()
    rowsList = []
    for i in range(0, len(rows)):
        rowsList.append(list(rows[i]))
    for i in range(0, len(rowsList)):
        rowsList[i][2] = rowsList[i][2].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[i][3]:
            rowsList[i][3] = rowsList[i][3].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[i][5]:
            rowsList[i][5] = int(rowsList[i][5].total_seconds() * 1000000)
    cur.close()
    con.close()
    return render(request, 'Replicate.html', {"rows": rowsList})