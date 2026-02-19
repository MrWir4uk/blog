from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),  # деталі поста
    path('create/', views.create_post, name='create_post'),  # створення поста
    path('profile/', views.profile_view, name='profile'),  # мій профіль
]
