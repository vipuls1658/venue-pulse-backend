from django.urls import path

from .views import TransactionViewSet

urlpatterns = [
    path(
        "transactions/",
        TransactionViewSet.as_view(actions={"post": "create"}),
        name="transaction-create",
    ),
]
