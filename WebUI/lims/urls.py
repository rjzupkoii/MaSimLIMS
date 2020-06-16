## 
# urls.py
#
# Define the URLS that are used by the LIMS.
##

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('study', views.study, name='study'),
    path('replicatesLatest100', views.replicatesLatest100, name='replicatesLatest100'),
    path('setdb/<int:id>', views.setdb, name='setdb'),
    # Get id
    path('StudyConfig/<str:id>',views.StudyConfig,name = 'StudyConfig'),
    path('StudyReplicate/<str:id>',views.StudyReplicate,name = 'StudyReplicate'),
    path('study/InsertFail', views.setStudyInsert, name='setStudyInsert'),
    path('study/DeleteFail/<str:id>', views.DeleteFail, name='DeleteFaile'),
    path('ConfigReplicate/<str:id>', views.ConfigReplicate, name = "ConfigReplicate"),
    path('worthToNotice', views.worthToNotice, name = "worthToNotice"),
]
