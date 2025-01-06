from django.urls import path
from cart import views
urlpatterns = [
    
    path('cart/',views.cart,name='cart'),
    path('addcart/<int:id>/<str:size>',views.addcart,name='addcart'),
    path('deletecart/<int:id>',views.deletecart,name='deletecart'),
    path('chectout/',views.chectout,name='checkout'),
    path('update_cart/<int:id>/',views.update_cart,name='update_cart'),

    
]