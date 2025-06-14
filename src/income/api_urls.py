from django.urls import path

from src.income import api_views

app_name = 'income'

urlpatterns = [
    path(
        "providers/",
        api_views.ProviderViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        "providers/<int:pk>/",
        api_views.ProviderViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update",
                "delete": "destroy",
            }
        ),
        name='provider-detail'
    ),
    path(
        "providers/<int:pk>/products/",
        api_views.ProviderViewSet.as_view(
            {
                "get": "get_products",
            }
        )
    ),
    path(
        "incomes/",
        api_views.IncomeViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        )
    ),
    path(
        "incomes/summary/",
        api_views.IncomeViewSet.as_view(
            {
                "get": "get_summary",
            }
        )
    ),
    path(
        "incomes/<int:pk>/",
        api_views.IncomeViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update",
                "delete": "destroy"
            }
        ),
        name='income-detail'
    ),
    path("incomes/<int:pk>/update-status/", api_views.IncomeUpdateStatusView.as_view()),
    path(
        "incomes/<int:income_id>/income-items/",
        api_views.IncomeItemViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        "incomes/<int:income_id>/income-items/multiple_create/",
        api_views.IncomeItemViewSet.as_view(
            {
                "post": "multiple_create"
            }
        )
    ),
    path(
        "incomes/<int:income_id>/income-items/multiple_update/",
        api_views.IncomeItemViewSet.as_view(
            {
                "put": "multiple_update"
            }
        )
    ),
    path(
        "incomes/<int:income_id>/income-items/<int:pk>/",
        api_views.IncomeItemViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update",
                # "patch": "partial_update",
                "delete": "destroy",
            }
        )
    ),
    path("incomes/statuses/", api_views.IncomeStatusOptionsView.as_view())
]
