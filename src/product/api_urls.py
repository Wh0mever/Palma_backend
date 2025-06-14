from django.urls import path
from src.product import api_views

app_name = 'product'

urlpatterns = [
    path(
        "products/",
        api_views.ProductViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        "products/composites/",
        api_views.ProductCompositeListView.as_view()
    ),
    path(
        "products/for-sale-list/",
        api_views.ProductViewSet.as_view(
            {
                "get": "get_for_sale_products",
            }
        )
    ),
    path(
        "products/<int:pk>/",
        api_views.ProductViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update",
                # "patch": "partial_update",
                "delete": "destroy"
            }
        ),
        name='product-detail'
    ),
    path(
        "products/<int:pk>/income-history/",
        api_views.ProductViewSet.as_view(
            {
                "get": "get_product_income_history",
            }
        )
    ),
    path(
        "products/<int:pk>/add-provider/",
        api_views.ProductViewSet.as_view(
            {
                "post": "add_provider"
            }
        )
    ),
    path(
        "products/<int:pk>/remove-provider/",
        api_views.ProductViewSet.as_view(
            {
                "post": "delete_provider"
            }
        )
    ),
    path(
        "industries/",
        api_views.IndustryViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        )
    ),
    path(
        "industries/<int:pk>/",
        api_views.IndustryViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update",
                "delete": "destroy"
            }
        ),
        name='industry-detail'
    ),
    path(
        "categories/",
        api_views.CategoryViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        "categories/for-sale/",
        api_views.CategoryViewSet.as_view(
            {
                "get": "for_sale_list",
            }
        )
    ),
    path(
        "categories/composite/",
        api_views.CategoryViewSet.as_view(
            {
                "get": "composite_list",
            }
        )
    ),
    path(
        "categories/<int:pk>/",
        api_views.CategoryViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update",
                "delete": "destroy"
            }
        ),
        name='category-detail'
    ),

    path("products/options/", api_views.ProductOptionsView.as_view()),
]
