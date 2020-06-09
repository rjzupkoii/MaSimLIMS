from django.shortcuts import render, redirect
import psycopg2
from django.http import HttpResponse
from django.contrib import messages

# Create your views here.
def studyMasim(request):
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="masim",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    # execute query
    sql = "SELECT studyid, CASE WHEN name IS NULL THEN 'Unassigned' ELSE name END, configs, replicates FROM " \
          "(SELECT studyid, s.name, COUNT(c.id) configs, COUNT(r.id) replicates " \
          "FROM sim.configuration c LEFT JOIN sim.replicate r ON r.configurationid = c.id LEFT JOIN sim.study s ON s.id = c.studyid GROUP BY studyid, s.name) iq order by studyid"
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    # close the connection
    con.close()
    return render(request,"index.html",{"rows": rows, "link": "Masim"})

def studyBurkinaFaso(request):
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="burkinafaso",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    sql = "SELECT studyid, CASE WHEN name IS NULL THEN 'Unassigned' ELSE name END, configs, replicates FROM " \
          "(SELECT studyid, s.name, COUNT(c.id) configs, COUNT(r.id) replicates " \
          "FROM sim.configuration c LEFT JOIN sim.replicate r ON r.configurationid = c.id LEFT JOIN sim.study s ON s.id = c.studyid GROUP BY studyid, s.name) iq order by studyid"
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    con.close()
    return render(request,"index.html",{"rows": rows, "link": "BurkinaFaso"})

def studyMasimInsert(request):
    # Here just switch the connection will be fine
    con = psycopg2.connect(
        host="localhost",
        database="LHJ",
        user="postgres",
        password="1234")
    # catch the error message
    try:
        cur = con.cursor()
        cur.execute("select * from study order by id")
        rows = cur.fetchall()
        cur.close()
        # When the user clicks "Submit" the form should check to see if a name was entered (i.e., more than 1 character), if it is valid then it is submitted to the server.
        name = request.POST["studyName"]
        # This works but need real database
        if len(name) < 1:
            raise Exception("Please input at least one character!")
        cur = con.cursor()
        # IDValue is used to find the lowest index which can be used.
        IDValue = 1
        # Get current database's current last ID
        lastID = rows[-1][0]
        # Get all ID values in the database.
        IDList = []
        # Append IDs to the list.
        for i in range(0, len(rows)):
            # Get each ID.
            IDList.append(rows[i][0])
        # Reuse the primary key.
        while IDValue <= lastID:
            # If find available ID.
            if IDValue not in IDList:
                sql = "insert into Study values (%s, %s)"
                cur.execute(sql, (str(IDValue), name))
                break
            IDValue+=1
        # If can't find avaiable ID
        if IDValue > lastID:
            sql = "insert into Study values (%s, %s)"
            cur.execute(sql, (str(lastID+1),name))
        con.commit()
        cur.close()
        '''
        cur = con.cursor()
        sql = "SELECT studyid, CASE WHEN name IS NULL THEN 'Unassigned' ELSE name END, configs, replicates FROM " \
          "(SELECT studyid, s.name, COUNT(c.id) configs, COUNT(r.id) replicates " \
          "FROM sim.configuration c LEFT JOIN sim.replicate r ON r.configurationid = c.id LEFT JOIN sim.study s ON s.id = c.studyid GROUP BY studyid, s.name) iq"
        rows = cur.fetchall()
        cur.close()'''
        con.close()
    except (Exception, psycopg2.DatabaseError) as error:
        messages.success(request, error)
        return render(request,"index.html",{"rows": rows, "link": "Masim"})
    return redirect('/Study/Masim')

def studyBurkinaFasoInsert(request):
    # Here just switch the connection will be fine
    con = psycopg2.connect(
        host="localhost",
        database="LHJ",
        user="postgres",
        password="1234")
    # catch the error message
    try:
        cur = con.cursor()
        cur.execute("select * from study order by id")
        rows = cur.fetchall()
        cur.close()
        # When the user clicks "Submit" the form should check to see if a name was entered (i.e., more than 1 character), if it is valid then it is submitted to the server.
        name = request.POST["studyName"]
        # This works but need real database
        if len(name) < 1:
            raise Exception("Please input at least one character!")
        cur = con.cursor()
        # IDValue is used to find the lowest index which can be used.
        IDValue = 1
        # since id is ordered, so lastID is the last ID.
        lastID = rows[-1][0]
        # Get all ID values in the database.
        IDList = []
        # Append IDs to the list.
        for i in range(0, len(rows)):
            # Get each ID.
            IDList.append(rows[i][0])
        # Reuse the primary key.
        while IDValue <= lastID:
            # If find available ID.
            if IDValue not in IDList:
                sql = "insert into Study values (%s, %s)"
                cur.execute(sql, (str(IDValue), name))
                break
            IDValue+=1
        # If can't find avaiable ID
        if IDValue > lastID:
            sql = "insert into Study values (%s, %s)"
            cur.execute(sql, (str(lastID + 1), name))
        con.commit()
        cur.close()
        '''
        cur = con.cursor()
        sql = "SELECT studyid, CASE WHEN name IS NULL THEN 'Unassigned' ELSE name END, configs, replicates FROM " \
          "(SELECT studyid, s.name, COUNT(c.id) configs, COUNT(r.id) replicates " \
          "FROM sim.configuration c LEFT JOIN sim.replicate r ON r.configurationid = c.id LEFT JOIN sim.study s ON s.id = c.studyid GROUP BY studyid, s.name) iq"
        rows = cur.fetchall()
        cur.close()'''
        con.close()
    except (Exception, psycopg2.DatabaseError) as error:
        messages.success(request, error)
        return render(request, "index.html", {"rows": rows, "link": "BurkinaFaso"})
    return redirect('/Study/BurkinaFaso')
def studyMasimDelete(request):
    ID = request.path.replace('/Study/Masim/DeleteFail/WhereStudyID=','')
    # Here just switch the connection will be fine
    con = psycopg2.connect(
        host="localhost",
        database="LHJ",
        user="postgres",
        password="1234")
    cur = con.cursor()
    sql = "Delete from study where id = " + ID
    cur.execute(sql)
    con.commit()
    cur.close()
    con.close()
    return redirect('/Study/Masim')

def studyBurkinaFasoDelete(request):
    ID = request.path.replace('/Study/BurkinaFaso/DeleteFail/WhereStudyID=','')
    # Here just switch the connection will be fine
    con = psycopg2.connect(
        host="localhost",
        database="LHJ",
        user="postgres",
        password="1234")
    cur = con.cursor()
    sql = "Delete from study where id = " + ID
    cur.execute(sql)
    con.commit()
    cur.close()
    con.close()
    return redirect('/Study/BurkinaFaso')