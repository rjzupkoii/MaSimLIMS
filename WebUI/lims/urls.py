## 
# urls.py
#
# Define the URLS that are used by the LIMS.
##

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('replicates', views.replicates, name='replicates'),
    path('setdb/<int:id>', views.setdb, name='setdb')
]
