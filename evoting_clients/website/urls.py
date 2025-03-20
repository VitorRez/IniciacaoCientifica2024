from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('create_elections/', views.create_elections, name='create_elections'),
    path('create_voters/', views.create_voters, name='create_voters'),
    path('create_offices/', views.create_offices, name='create_offices'),
    path('election/', views.election_page, name='election'),
    path('authenticate/', views.authentication_page, name='authenticate'),
    path('commit/', views.commit_page, name='commit'),
    path('apply/', views.applying_page, name='apply'),
    path('voting/', views.voting_page, name='voting'),
    path('voting_submit', views.voting_submit, name='voting_submit'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('ajax/load-offices/', views.load_offices, name='ajax_load_offices'),
]

