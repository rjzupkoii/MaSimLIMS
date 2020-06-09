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

# cursor
cur = con.cursor()
cur.execute("select id from configuration")
IDConfig = cur.fetchall()
cur.close()

# close the con
con.close()

urlpatterns = []
for i in ID:
    urlpatterns.append(path('Masim/WhereStudyID='+str(i[0]), views.replicateMasimStudy, name='replicateMasimStudy'))
urlpatterns.append(path('Masim/WhereStudyID=None', views.replicateMasimStudy, name='replicateMasimStudyNone'))

for i in IDConfig:
    urlpatterns.append(path('Masim/WhereConfigID='+str(i[0]), views.replicateMasimConfig, name='replicateMasimConfig'))
urlpatterns.append(path('Masim/WhereConfigID=None', views.replicateMasimConfig, name='replicateMasimConfigNone'))

urlpatterns.append(path('Masim/WorthToNotice',views.replicateMasimWorth, name='replicateMasimWorth'))

con = psycopg2.connect(
        host="masimdb.vmhost.psu.edu",
        database="burkinafaso",
        user="sim",
        password="sim")
# cursor
cur = con.cursor()
cur.execute("select id from study")
ID = cur.fetchall()
# close the cursor
cur.close()
# cursor
cur = con.cursor()
cur.execute("select id from configuration")
IDConfig = cur.fetchall()
cur.close()
# close the con
con.close()
for i in ID:
    urlpatterns.append(path('BurkinaFaso/WhereStudyID='+str(i[0]), views.replicateBurkinaFasoStudy, name='replicateBurkinaFasoStudy'))
urlpatterns.append(path('BurkinaFaso/WhereStudyID=None', views.replicateBurkinaFasoStudy, name='replicateBurkinaFasoStudyNone'))

for i in IDConfig:
    urlpatterns.append(path('BurkinaFaso/WhereConfigID='+str(i[0]), views.replicateBurkinaFasoConfig, name='replicateBurkinaFasoConfig'))
urlpatterns.append(path('BurkinaFaso/WhereConfigID=None', views.replicateBurkinaFasoConfig, name='replicateBurkinaFasoConfigNone'))

urlpatterns.append(path('BurkinaFaso/WorthToNotice',views.replicateBurkinaFasoWorth, name='replicateBurkinaFasoWorth'))