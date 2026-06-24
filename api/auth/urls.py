from django.urls import path

from api.auth.views import AuthViewSet

urlpatterns = [
    path(
        "auth/login/",
        AuthViewSet.as_view(actions={"post": "login"}),
        name="auth-login",
    ),
    path(
        "auth/refresh/",
        AuthViewSet.as_view(actions={"post": "refresh"}),
        name="auth-refresh",
    ),
]
