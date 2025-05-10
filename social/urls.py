from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_view, name='upload'),
    path('comment/<int:post_id>/', views.add_comment, name='comment'),
    path('like/<int:post_id>/', views.like_post, name='like'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
] 