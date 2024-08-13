from django.urls import path
from .views import AuthenticateVoterView, ApplyingView, OfficesListView, ElectionListView

urlpatterns = [
    path("voter-authentication/", AuthenticateVoterView.as_view(), name="voter-authentication"),
    path("apply/", ApplyingView.as_view(), name="apply"),
    path("offices/", OfficesListView.as_view(), name='offices-list'),
    path("elections/", ElectionListView.as_view(), name="election-list"),
]
