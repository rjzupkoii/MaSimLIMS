## 
# urls.py
#
# Define the URLS that are used by the LIMS.
##

from django.urls import path
from rest_framework import routers, serializers, viewsets
from . import views

# Add urls, their implementation function in views, and their names.
urlpatterns = [
    path('', views.index, name='index'),

    path('ConfigReplicate/<str:id>', views.ConfigReplicate, name = "ConfigReplicate"),

    path('createDatabase', views.createDatabase, name='createDatabase'),
    path('createNewDatabase', views.createNewDatabase, name='createNewDatabase'),
    path('longRunningDelete', views.longRunningDelete, name='longRunningDelete'),

    path('setdb/<int:id>', views.setdb, name='setdb'),

    path('study', views.study, name='study'),
    path('Study/Chart/<str:studyId>', views.studyChart, name = "studyChart"),
    path('study/DeleteFail/<str:id>', views.DeleteFail, name='DeleteFaile'),
    path('Study/DeleteNotes/<str:studyId>/<str:id>', views.DeleteNotes, name = "DeleteNotes"),
    path('study/InsertFail', views.setStudyInsert, name='setStudyInsert'),
    path('Study/Notes/<str:studyId>', views.studyNotes, name = "studyNotes"),
    path('Study/NotesRecord/<str:studyId>', views.studyNotesRecord, name = "studyNotesRecord"),
    
    path('StudyConfig/<str:id>',views.StudyConfig,name = 'StudyConfig'),
    path('StudyReplicate/<str:id>',views.StudyReplicate,name = 'StudyReplicate'),

    path('replicatesLatest100', views.replicatesLatest100, name='replicatesLatest100'),
    
    path('worthToNotice', views.worthToNotice, name = "worthToNotice"),
]
