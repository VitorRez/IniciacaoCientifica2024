from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('authenticate/', views.authentication_page, name='authenticate'),
    path('commit/', views.commit_page, name='commit'),
    path('apply/', views.applying_page, name='apply'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('ajax/load-offices/', views.load_offices, name='ajax_load_offices'),
]
