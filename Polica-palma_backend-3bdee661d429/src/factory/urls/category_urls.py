from django.urls import path

from .. import api_views

app_name = 'factory_category'

urlpatterns = [
    path(
        'product-factory-categories/',
        api_views.ProductFactoryCategoryViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        'product-factory-categories/<int:pk>/',
        api_views.ProductFactoryCategoryViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update",
                "delete": "destroy"
            }
        )
    )
]
