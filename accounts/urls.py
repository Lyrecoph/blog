from django.urls import path

from accounts import views

urlpatterns = [
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('register/', views.register_view, name='register_view'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('editProfile/', views.editProfile, name='edit_profile'),
]
