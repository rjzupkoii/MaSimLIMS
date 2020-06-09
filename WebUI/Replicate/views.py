from django.shortcuts import render
from datetime import datetime
# Create your views here.
import psycopg2
# Create your views here.
# Try to check end time and running time whether exist "strftime"
# Masim operations
def replicateMasimStudy(request):
    studyID = request.path.replace('/Replicate/Masim/WhereStudyID=','')
    if studyID == "None":
        studyID = "NULL"
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="masim",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    # sql
    if studyID == "NULL":
        sql = "select v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime " \
              "from configuration inner join v_replicates on v_replicates.configurationid = configuration.id where studyid is NULL order by v_replicates.id"
    else:
        sql = "select v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime from study left join configuration on configuration.studyID = "\
              + studyID + "inner join v_replicates on v_replicates.configurationid = configuration.id where study.id = " + studyID + "order by v_replicates.id"
    cur.execute(sql)
    rows = cur.fetchall()
    rowsList = []
    for i in range(0,len(rows)):
        rowsList.append(list(rows[i]))
    for i in range(0,len(rowsList)):
        rowsList[i][2] = rowsList[i][2].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[i][3]:
            rowsList[i][3] = rowsList[i][3].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[i][5]:
            rowsList[i][5] = int(rowsList[i][5].total_seconds()* 1000000)
    cur.close()
    con.close()
    return render(request,'Replicate.html',{"rows":rowsList})

def replicateMasimConfig(request):
    configID = request.path.replace('/Replicate/Masim/WhereConfigID=', '')
    if configID == "None":
        configID = "NULL"
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="masim",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    # sql
    if configID == "NULL":
        sql = "select v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime " \
              "from v_replicates where configurationid is NULL order by v_replicates.id"
    else:
        sql = "select v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime " \
              "from v_replicates where configurationid = " + configID + "order by v_replicates.id"
    cur.execute(sql)
    rows = cur.fetchall()
    rowsList = []
    for i in range(0,len(rows)):
        rowsList.append(list(rows[i]))
    for i in range(0,len(rowsList)):
        rowsList[i][2] = rowsList[i][2].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[i][3]:
            rowsList[i][3] = rowsList[i][3].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[i][5]:
            rowsList[i][5] = int(rowsList[i][5].total_seconds()* 1000000)
    cur.close()
    con.close()
    return render(request,'Replicate.html',{"rows":rowsList})

def replicateMasimWorth(request):
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="masim",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    sql = "select id, filename, starttime, endtime, movement, runningtime from v_replicates " \
          "where starttime < (SELECT min(starttime) FROM (SELECT starttime FROM v_replicates ORDER BY starttime DESC LIMIT 100) last100) " \
          "and (now()-starttime) > interval '2 days' and endtime is null order by id desc"
    cur.execute(sql)
    rows = cur.fetchall()
    rowsList = []
    for i in range(0, len(rows)):
        rowsList.append(list(rows[i]))
    for i in range(0,len(rowsList)):
        rowsList[i][2] = rowsList[i][2].strftime("%m/%d/%Y, %H:%M:%S")
        rowsList[i][3] = rowsList[i][3]
        rowsList[i][5] = rowsList[i][5]
    cur.close()
    con.close()
    return render(request, 'Replicate.html', {"rows": rowsList})

# Burkina Faso operation
def replicateBurkinaFasoStudy(request):
    studyID = request.path.replace('/Replicate/BurkinaFaso/WhereStudyID=', '')
    if studyID == "None":
        studyID = "NULL"
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="burkinafaso",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    # sql
    if studyID == "NULL":
        sql = "select v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime " \
              "from configuration inner join v_replicates on v_replicates.configurationid = configuration.id where studyid is NULL order by v_replicates.id"
    else:
        sql = "select v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime from study left join configuration on configuration.studyID = " \
              + studyID + "inner join v_replicates on v_replicates.configurationid = configuration.id where study.id = " + studyID + "order by v_replicates.id"
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

def replicateBurkinaFasoConfig(request):
    configID = request.path.replace('/Replicate/BurkinaFaso/WhereConfigID=', '')
    if configID == "None":
        configID = "NULL"
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="burkinafaso",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    # sql
    if configID == "NULL":
        sql = "select v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime " \
              "from v_replicates where configurationid is NULL order by v_replicates.id"
    else:
        sql = "select v_replicates.id, v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime " \
              "from v_replicates where configurationid = " + configID + "order by v_replicates.id"
    cur.execute(sql)
    rows = cur.fetchall()
    rowsList = []
    for i in range(0,len(rows)):
        rowsList.append(list(rows[i]))
    for i in range(0,len(rowsList)):
        rowsList[i][2] = rowsList[i][2].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[i][3]:
            rowsList[i][3] = rowsList[i][3].strftime("%m/%d/%Y, %H:%M:%S")
        if rowsList[i][5]:
            rowsList[i][5] = int(rowsList[i][5].total_seconds()* 1000000)
    cur.close()
    con.close()
    return render(request,'Replicate.html',{"rows":rowsList})

def replicateBurkinaFasoWorth(request):
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="burkinafaso",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    sql = "select id, filename, starttime, endtime, movement, runningtime from v_replicates " \
          "where starttime < (SELECT min(starttime) FROM (SELECT starttime FROM v_replicates ORDER BY starttime DESC LIMIT 100) last100) " \
          "and (now()-starttime) > interval '2 days' and endtime is null order by id desc"
    cur.execute(sql)
    rows = cur.fetchall()
    rowsList = []
    for i in range(0, len(rows)):
        rowsList.append(list(rows[i]))
    for i in range(0,len(rowsList)):
        rowsList[i][2] = rowsList[i][2].strftime("%m/%d/%Y, %H:%M:%S")
        rowsList[i][3] = rowsList[i][3]
        rowsList[i][5] = rowsList[i][5]
    cur.close()
    con.close()
    return render(request, 'Replicate.html', {"rows": rowsList})