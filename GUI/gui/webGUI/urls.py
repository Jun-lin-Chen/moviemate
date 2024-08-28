from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.helloworld, name = 'helloworld'),
    path("index/", views.index_view, name = 'index'),
]