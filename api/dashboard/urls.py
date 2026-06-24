from django.urls import path

from .views import DashboardViewSet

urlpatterns = [
    path(
        "dashboard/venue-sales/",
        DashboardViewSet.as_view(actions={"get": "venue_sales"}),
        name="dashboard-venue-sales",
    ),
    path(
        "dashboard/top-items/",
        DashboardViewSet.as_view(actions={"get": "top_items"}),
        name="dashboard-top-items",
    ),
    path(
        "dashboard/alerts/",
        DashboardViewSet.as_view(actions={"get": "alerts"}),
        name="dashboard-alerts",
    ),
    path(
        "dashboard/hourly-sales/",
        DashboardViewSet.as_view(actions={"get": "hourly_sales"}),
        name="dashboard-hourly-sales",
    ),
    path(
        "dashboard/venue/",
        DashboardViewSet.as_view(actions={"get": "venue_detail"}),
        name="dashboard-venue-detail",
    ),
]
