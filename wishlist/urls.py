from django.urls import path
from wishlist import views
urlpatterns = [
    
  path('wishlist',views.wishlist,name='wishlist'),
  path('add_wishlist/<int:id>/',views.add_wishlist,name='add_wishlist'),
  path('delete_wishlist/<int:id>/',views.delete_wishlist,name="delete_wishlist"),
  path('add_wishlist_from_product_details/<int:id>/<str:size>/',views.add_wishlist_from_product_details,name='add_wishlist_from_product_details'),
  path('wishlist_to_cart/<int:id>/',views.wishlist_to_cart,name='wishlist_to_cart'),
  
]