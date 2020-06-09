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

urlpatterns = [
    path('', views.studyMasim, name='studyMasim'),
    path('Masim', views.studyMasim, name='studyMasim'),
    path('BurkinaFaso', views.studyBurkinaFaso, name = 'studyBurkinaFaso'),
    path('Masim/InsertFail', views.studyMasimInsert, name='studyMasimInsert'),
    path('BurkinaFaso/InsertFail', views.studyBurkinaFasoInsert, name = 'studyBurkinaFasoInsert'),
]
'''Get all available id from the database and append it to path.'''
for i in ID:
    urlpatterns.append(path('Masim/DeleteFail/WhereStudyID='+str(i[0]), views.studyMasimDelete, name='studyMasimDelete'))

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
     urlpatterns.append(path('BurkinaFaso/DeleteFail/WhereStudyID='+str(i[0]), views.studyBurkinaFasoDelete, name='studyBurkinaFasoDelete'))