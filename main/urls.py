from django.urls import path
from . import views
from django.urls import include, path

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),  # деталі поста
    path('create/', views.create_post, name='create_post'),  # створення поста
    path('profile/', views.profile_view, name='profile'),  # мій профіль
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('my-drafts/', views.my_drafts, name='my_drafts'), # мої чернетки
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'), # редагування поста
    path("select2/", include("django_select2.urls")), 
    path('comment/<int:pk>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('ckeditor/', include('ckeditor_uploader.urls')), 
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('draft/<int:draft_id>/delete/', views.delete_draft, name='delete_draft'),
    path('post/<int:post_id>/rate/<int:value>/', views.rate_post, name='rate_post'),

]
