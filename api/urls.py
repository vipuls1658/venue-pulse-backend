from django.urls import include, path

# Each feature owns its own urls; the api app stitches them together.
urlpatterns = [
    path("", include("api.auth.urls")),
    path("", include("api.transactions.urls")),
    path("", include("api.dashboard.urls")),
]
