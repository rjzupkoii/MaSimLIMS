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
    path('worthToNotice', views.worthToNotice, name = "worthToNotice"),

    # Put id in the urls
    path('setdb/<int:id>', views.setdb, name='setdb'),
    path('StudyConfig/<str:id>',views.StudyConfig,name = 'StudyConfig'),
    path('StudyReplicate/<str:id>',views.StudyReplicate,name = 'StudyReplicate'),
    path('study/InsertFail', views.setStudyInsert, name='setStudyInsert'),
    path('study/DeleteFail/<str:id>', views.DeleteFail, name='DeleteFaile'),
    path('ConfigReplicate/<str:id>', views.ConfigReplicate, name = "ConfigReplicate"),
]
