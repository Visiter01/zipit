# zipit/urls.py
from django.urls import path
from . import views

app_name = 'zipit'

urlpatterns = [
    path('', views.home, name='home'),
    path('compress/', views.compress_file, name='compress_file'),
    path('decompress/', views.decompress_file, name='decompress_file'),
]