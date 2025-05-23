"""ecommerce_project URL Configuration

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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls import include
from auth_user import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include('auth_user.urls')),
    path('accounts/',include('allauth.urls')),
    path('admin_auth/',include('admin_auth.urls')),
    path('catagory/',include('Catagory.urls')),
    path('products/',include('products.urls')),
    path('profile/',include('userprofile.urls')),
    path('carts/',include('cart.urls')),
    path('order/',include('order.urls')),
    path('wishlist/',include('wishlist.urls')),
    path('Coupons/',include('Coupons.urls')),
    path('transcation/',include('transaction.urls')),
    path('accounts/', include('allauth.urls')),

    # ==========================================================================================
    path('',views.home,name='index')
   
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

