from django.urls import path
from src.warehouse import api_views

app_name = 'warehouse'

urlpatterns = [
    path(
        "warehouse/",
        api_views.WarehouseProductViewSet.as_view(
            {
                "get": "list",
            }
        )
    ),
    path(
        "warehouse/summary/",
        api_views.WarehouseProductViewSet.as_view(
            {
                "get": "get_summary",
            }
        )
    ),
    path(
        "warehouse/export-excel/<int:user_id>/",
        api_views.WarehouseProductViewSet.as_view(
            {
                "get": "export_excel",
            }
        )
    ),
    path(
        "warehouse/composites/",
        api_views.WarehouseProductCompositeListView.as_view()
    ),
    path(
        "warehouse/<int:pk>/",
        api_views.WarehouseProductViewSet.as_view(
            {
                "get": "retrieve",
            }
        )
    ),
    path(
        "warehouse/write-offs/",
        api_views.WarehouseProductWriteOffViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        "warehouse/write-offs/<int:pk>/",
        api_views.WarehouseProductWriteOffViewSet.as_view(
            {
                "get": "retrieve",
                "delete": "destroy"
            }
        )
    ),
]
