from django.urls import path
from . import views
from accounts.views import register

urlpatterns = [
    path('products/', views.product_list, name = 'product_list'),
    path('cart/', views.view_cart, name = 'view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name  = 'add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name = 'remove_from_cart'),
    path('checkout/', views.checkout, name = 'checkout'),
    path('cart/add_item/<int:product_id>/', views.add_item, name = 'add_item'),

]
