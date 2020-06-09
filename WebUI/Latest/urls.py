from django.urls import path
from . import views
urlpatterns = [
    path('Masim', views.latestMasim, name='latestMasim'),
    path('BurkinaFaso', views.latestBurkinaFaso, name = 'latestBurkinaFaso')
]
