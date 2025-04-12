from django.urls import path 
from . import views

urlpatterns =[
    path('', views.home, name='home'),
    path('add-to-cart/<int:coffee_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/increment/<int:cart_id>/', views.increment_quantity, name='increment_quantity'),
    path('cart/decrement/<int:cart_id>/', views.decrement_quantity, name='decrement_quantity'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
]