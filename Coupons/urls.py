from django.urls import path
from Coupons import views
urlpatterns = [
    path('list_coupons/',views.list_coupons,name='list_coupons'),
    path('create_coupons/',views.create_coupons,name='create_coupons'),
    path('edit_coupon/<int:id>/',views.edit_coupon,name='edit_coupon'),
    path('remove_coupon/',views.remove_coupon,name='remove_coupon'),
    

]