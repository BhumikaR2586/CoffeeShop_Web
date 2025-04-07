from django.urls import path 
from . import views

urlpatterns =[
    path('', views.home, name='home'),
    path('add-to-cart/<int:coffee_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/increment/<int:cart_id>/', views.increment_quantity, name='increment_quantity'),
    path('cart/decrement/<int:cart_id>/', views.decrement_quantity, name='decrement_quantity'),
]