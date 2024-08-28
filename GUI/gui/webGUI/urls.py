from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.helloworld, name = 'helloworld'),
    path("index/", views.index_view, name = 'index'),
    path("post/", views.post_view, name='post'),
    path("author/", views.author_view, name='author'),

]