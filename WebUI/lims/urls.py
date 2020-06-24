## 
# urls.py
#
# Define the URLS that are used by the LIMS.
##

from django.urls import path
from . import views

# Add urls, their implementation function in views, and their names.
urlpatterns = [
    path('', views.index, name='index'),
    path('study', views.study, name='study'),
    path('replicatesLatest100', views.replicatesLatest100, name='replicatesLatest100'),
    path('setdb/<int:id>', views.setdb, name='setdb'),
    # Put id in the urls
    path('StudyConfig/<str:id>/<str:studyname>',views.StudyConfig,name = 'StudyConfig'),
    path('StudyReplicate/<str:id>/<str:studyname>',views.StudyReplicate,name = 'StudyReplicate'),
    path('study/InsertFail', views.setStudyInsert, name='setStudyInsert'),
    path('study/DeleteFail/<str:id>', views.DeleteFail, name='DeleteFaile'),
    path('ConfigReplicate/<str:id>/<str:configurationName>', views.ConfigReplicate, name = "ConfigReplicate"),
    path('worthToNotice', views.worthToNotice, name = "worthToNotice"),
    path('Study/Notes/<str:studyId>/<str:studyName>', views.studyNotes, name = "studyNotes"),
    path('Study/NotesRecord/<str:studyId>/<str:studyName>', views.studyNotesRecord, name = "studyNotesRecord"),

    path('Study/DeleteNotes/<str:studyId>/<str:id>/<str:studyName>', views.DeleteNotes, name = "DeleteNotes"),
]
