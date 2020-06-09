from django.shortcuts import render
import psycopg2
# Create your views here.
def runningMasim(request):
    # within first 100, start within two days, and endtime is Null.
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="masim",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    sql = "SELECT id, filename, starttime, endtime, movement, runningtime " \
          "FROM (SELECT * FROM v_replicates ORDER BY starttime DESC LIMIT 100) last100 where (now()-starttime) <= interval '2 days' and endtime is null order by id desc"
    cur.execute(sql)
    rows = cur.fetchall()
    if len(rows) == 0:
        cur.close()
        con.close()
        return render(request,"Empty.html",{"Message": "masim, no rows running"})
    else:
        rowsList = []
        for i in range(0, len(rows)):
            rowsList.append(list(rows[i]))
        for i in range(0, len(rowsList)):
            rowsList[i][2] = rowsList[i][2].strftime("%m/%d/%Y, %H:%M:%S")
            rowsList[i][3] = rowsList[i][3]
            rowsList[i][5] = rowsList[i][5]
        cur.close()
        con.close()
        return render(request, 'Replicate.html', {"rows": rowsList})
def runningBurkinaFaso(request):
    # within first 100, start within two days, and endtime is Null.
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="burkinafaso",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    sql = "SELECT id, filename, starttime, endtime, movement, runningtime " \
          "FROM (SELECT * FROM v_replicates ORDER BY starttime DESC LIMIT 100) last100 where (now()-starttime) <= interval '2 days' and endtime is null order by id desc"
    cur.execute(sql)
    rows = cur.fetchall()
    if len(rows) == 0:
        cur.close()
        con.close()
        return render(request,"Empty.html",{"Message": "burkinafaso, no rows running"})
    else:
        rowsList = []
        for i in range(0, len(rows)):
            rowsList.append(list(rows[i]))
        for i in range(0, len(rowsList)):
            rowsList[i][2] = rowsList[i][2].strftime("%m/%d/%Y, %H:%M:%S")
            rowsList[i][3] = rowsList[i][3]
            rowsList[i][5] = rowsList[i][5]
        cur.close()
        con.close()
        return render(request, 'Replicate.html', {"rows": rowsList})