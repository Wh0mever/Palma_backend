from django.urls import path

from .. import api_views

app_name = 'factory'

urlpatterns = [
    path(
        "product-factories/",
        api_views.ProductFactoryViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ), path(
        "product-factories/summary/",
        api_views.ProductFactoryViewSet.as_view(
            {
                "get": "get_summary",
            }
        )
    ),
    path(
        "product-factories/finished/",
        api_views.ProductFactoryViewSet.as_view(
            {
                "get": "finished_list",
            }
        )
    ),
    path(
        "product-factories/written-off/",
        api_views.ProductFactoryViewSet.as_view(
            {
                "get": "written_off_list",
            }
        )
    ),
    path(
        "product-factories/written-off/summary/",
        api_views.ProductFactoryViewSet.as_view(
            {
                "get": "written_off_summary",
            }
        )
    ),
    path(
        "product-factories/for-sale/",
        api_views.ProductFactoryViewSet.as_view(
            {
                "get": "get_for_sale_list",
            }
        )
    ),
    path(
        "product-factories/florist/<int:florist_id>/",
        api_views.ProductFactoryViewSet.as_view(
            {
                "get": "get_by_florist"
            }
        )
    ),

    path(
        "product-factories/statuses/",
        api_views.ProductFactoryStatusOptionsView.as_view()
    ),
    path(
        "product-factories/sales-types/",
        api_views.ProductFactorySalesTypeOptionsView.as_view()
    ),
    path(
        "product-factories/<int:pk>/",
        api_views.ProductFactoryViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update",
                "delete": "destroy"
            }
        )
    ),
    path(
        "product-factories/<int:pk>/finish/",
        api_views.ProductFactoryViewSet.as_view(
            {
                "post": "finish"
            }
        )
    ),
    path(
        "product-factories/<int:pk>/write_off/",
        api_views.ProductFactoryViewSet.as_view(
            {
                "post": "write_off"
            }
        )
    ),
    path(
        "product-factories/<int:pk>/request_write_off/",
        api_views.ProductFactoryViewSet.as_view(
            {
                "post": "request_write_off"
            }
        )
    ),
    path(
        "product-factories/<int:pk>/request_return_to_create/",
        api_views.ProductFactoryViewSet.as_view(
            {
                "post": "request_return_to_create"
            }
        )
    ),
    path(
        "product-factories/<int:pk>/return_to_create/",
        api_views.ProductFactoryViewSet.as_view(
            {
                "post": "return_to_create"
            }
        )
    ),
    path(
        "product-factories/<int:product_factory_id>/items/",
        api_views.ProductFactoryItemViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        "product-factories/<int:product_factory_id>/items/<int:pk>/",
        api_views.ProductFactoryItemViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update",
                "delete": "destroy",
            }
        )
    ),
    path(
        "product-factories/<int:product_factory_id>/items/<int:pk>/write-off-product/",
        api_views.ProductFactoryItemViewSet.as_view(
            {
                "post": "write_off_product",
            }
        )
    ),
    path(
        "product-factories/<int:product_factory_id>/items/<int:item_id>/returns/",
        api_views.ProductFactoryItemReturnViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        "product-factories/<int:product_factory_id>/items/<int:item_id>/returns/<int:pk>/",
        api_views.ProductFactoryItemReturnViewSet.as_view(
            {
                "get": "retrieve",
                "delete": "destroy"
            }
        )
    ),
]
