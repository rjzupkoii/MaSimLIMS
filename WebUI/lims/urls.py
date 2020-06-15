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
    path('setStudyConfig/<str:id>',views.setStudyConfig,name = 'setStudyConfig'),
    path('setStudyReplicate/<str:id>',views.setStudyReplicate,name = 'setStudyReplicate'),
    path('config', views.config, name='config'),
    path('replicate', views.replicate, name='replicate'),
    path('study/InsertFail', views.setStudyInsert, name='setStudyInsert'),
    path('study/setStudyDelete/<str:id>', views.setStudyDelete, name='setStudyDelete'),
    path('study/DeleteFail', views.DeleteFail, name = "DeleteFail"),
    path('setConfigReplicate/<str:id>', views.setConfigReplicate, name = "setConfigReplicate"),
    path('configReplicate', views.configReplicate, name = "configReplicate"),
    path('worthToNotice', views.worthToNotice, name = "worthToNotice"),
]
