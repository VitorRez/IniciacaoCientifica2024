from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("templates/userpage.html", views.userpage, name="userpage")
]
