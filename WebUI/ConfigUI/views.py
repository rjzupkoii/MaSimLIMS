from django.shortcuts import render
import psycopg2
# Create your views here.
def configMasim(request):
    StudyID = request.path.replace('/Config/Masim/WhereStudyID=','')
    if StudyID == "None":
        # is NULL
        # Since replicates, sql syntax is correct!
        StudyID = "NULL"
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="masim",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    if StudyID == "NULL":
        cur.execute("select configuration.id, configuration.name, configuration.notes, configuration.filename," +
                    " concat('(', ncols, ', ', nrows, ', ', xllcorner, ', ', yllcorner, ', ', cellsize, ')') as spatial, count(replicate.id) " +
                    "from configuration left join replicate on replicate.configurationid = configuration.id where studyid is NULL group by configuration.id order by configuration.id")
    else:
        cur.execute("select configuration.id, configuration.name, configuration.notes, configuration.filename," +
                    " concat('(', ncols, ', ', nrows, ', ', xllcorner, ', ', yllcorner, ', ', cellsize, ')') as spatial, count(replicate.id) " +
                    "from configuration left join replicate on replicate.configurationid = configuration.id where studyid = " + StudyID + ' group by configuration.id order by configuration.id')
    rows = cur.fetchall()
    cur.close()
    con.close()

    return render(request,"Config.html", {'rows': rows, "link": "Masim"})

def configBurkinaFaso(request):
    StudyID = request.path.replace('/Config/BurkinaFaso/WhereStudyID=', '')
    if StudyID == "None":
        StudyID = "NULL"
    con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="burkinafaso",
        user="sim",
        password="sim")
    # cursor
    cur = con.cursor()
    if StudyID == "NULL":
        cur.execute("select configuration.id, configuration.name, configuration.notes, configuration.filename," +
                    " concat('(', ncols, ', ', nrows, ', ', xllcorner, ', ', yllcorner, ', ', cellsize, ')') as spatial, count(replicate.id) " +
                    "from configuration left join replicate on replicate.configurationid = configuration.id where studyid is NULL group by configuration.id order by configuration.id")
    else:
        cur.execute("select configuration.id, configuration.name, configuration.notes, configuration.filename," +
                    " concat('(', ncols, ', ', nrows, ', ', xllcorner, ', ', yllcorner, ', ', cellsize, ')') as spatial, count(replicate.id) " +
                    "from configuration left join replicate on replicate.configurationid = configuration.id where studyid = " + StudyID + 'group by configuration.id order by configuration.id')
    rows = cur.fetchall()
    cur.close()
    con.close()

    return render(request, "Config.html", {'rows': rows,"link": "BurkinaFaso"})