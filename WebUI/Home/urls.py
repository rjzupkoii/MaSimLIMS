from django.urls import path
from . import views
urlpatterns = [
    path('', views.runningMasim, name='runningMasimHome'),
    path('Masim', views.runningMasim, name='runningMasim'),
    path('BurkinaFaso', views.runningBurkinaFaso, name = 'runningBurkinaFaso')
]
