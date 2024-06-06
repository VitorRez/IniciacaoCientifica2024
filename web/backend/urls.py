from django.urls import path
from .views import VoterView, HomePageView

urlpatterns = [
    path('homepage', HomePageView.as_view()),
]