from django.urls import path
from django.views.generic import TemplateView

from product.views.product import CreateProductView
from product.views.variant import VariantView, VariantCreateView, VariantEditView

from .views.product import ProductCreateAPI, ProductList, ProductSearch, updateProduct

app_name = "product"

urlpatterns = [
    # Variants URLs
    path('variants/', VariantView.as_view(), name='variants'),
    path('variant/create', VariantCreateView.as_view(), name='create.variant'),
    path('variant/<int:id>/edit', VariantEditView.as_view(), name='update.variant'),

    # Products URLs
    path('create/', CreateProductView.as_view(), name='create.product'),
    path('list/', ProductList.as_view(), name='list.product'),
    path('search-result/', ProductSearch, name='product-search'),
    path('update-product/<int:id>/', updateProduct, name='update-product'),
    path('product-create/', ProductCreateAPI.as_view(), name='product-create')
]
