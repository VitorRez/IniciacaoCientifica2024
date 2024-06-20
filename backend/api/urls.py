from django.urls import path
from . import views

urlpatterns = [
    path("voter/", views.CreateVoterList.as_view(), name="create-voter"),
]
