from django.urls import path
from products import views

urlpatterns = [

    path('product_list/',views.product_list,name='product_list'),
    path('edit_product/<int:id>/',views.edit_product,name='edit_product'),
    path('create_product/',views.create_product,name='create_product'),
    path('unlist_product/<int:id>/',views.unlist_product,name='unlist_product'),
   # =============================================================================
   path('list_variant/<int:product_id>/',views.list_variant,name='list_variant'),
   path('create_variant/<int:product_id>/',views.create_variant,name='create_variant'),
   path('edit_variant/<int:variant>/',views.edit_variant,name='edit_variant'),

#    =================================USER=======================================================
  path('display_products/',views.display_products,name='display_products'),
  path('product_details/<int:id>',views.product_details,name='product_details'),
   

    
]