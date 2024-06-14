from django.urls import path
from .views import VoterView, AccessPageView

urlpatterns = [
    path('accesspage', AccessPageView.as_view()),
]