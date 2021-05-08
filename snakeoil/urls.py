"""snakeoil URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import permission_required
from django.urls import path

from snakeoil_webshop.views import (
    ShopView,
    AddToCartView,
    ClearCartView,
    ShoppingCartView,
    ProductManagementView
)


urlpatterns = [
    path("", ShopView.as_view(), name="shop"),
    path("manage/products/", permission_required('snakeoil_webshop.add_product')(ProductManagementView.as_view()), name="product-management"),
    path("cart/", ShoppingCartView.as_view(), name="shopping-cart"),
    path("cart/add/", AddToCartView.as_view(), name="add-to-cart"),
    path("cart/clear/", ClearCartView.as_view(), name="clear-cart"),

    path("admin/", admin.site.urls),
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]
