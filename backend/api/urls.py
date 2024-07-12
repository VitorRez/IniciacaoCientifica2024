from django.urls import path
from .views import AuthenticateVoterView, ApplyingView

urlpatterns = [
    path("voter-authentication/", AuthenticateVoterView.as_view(), name="voter-authentication"),
    path("apply/", ApplyingView.as_view() ,name="apply")
]
