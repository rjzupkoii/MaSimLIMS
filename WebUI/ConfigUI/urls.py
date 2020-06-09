from django.urls import path
from . import views
import psycopg2
con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="masim",
        user="sim",
        password="sim")
# cursor
cur = con.cursor()
cur.execute("select id from study")
ID = cur.fetchall()
# close the cursor
cur.close()
con.close()

urlpatterns = []
for i in ID:
    urlpatterns.append(path('Masim/WhereStudyID='+str(i[0]), views.configMasim, name='configMasim'))
urlpatterns.append(path('Masim/WhereStudyID=None', views.configMasim, name='configMasimNone'))

con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="burkinafaso",
        user="sim",
        password="sim")
cur = con.cursor()
cur.execute("select id from study")
ID = cur.fetchall()
# close the cursor
cur.close()
con.close()
for i in ID:
    urlpatterns.append(path('BurkinaFaso/WhereStudyID='+str(i[0]), views.configBurkinaFaso, name='configBurkinaFaso'))
urlpatterns.append(path('BurkinaFaso/WhereStudyID=None', views.configBurkinaFaso, name='configBurkinaFasoNone'))