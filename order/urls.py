from django.urls import path
from order import views
urlpatterns = [

    path('placeorder/',views.placeorder,name='placeorder'),
    path('orderlist/',views.orderlist,name='orderlist'),
    path('orderdetails/<int:id>/',views.orderdetails,name='orderdetails'),
    path('cancel_order/<int:id>/', views.cancel_order, name='cancel_order'), 
    path('add_address_checkout/',views.add_address_checkout,name='add_address_checkout'),
    path('review/<int:id>/<int:id2>/',views.review,name='review'),
    path('apply_coupon/',views.apply_coupon,name='apply_coupon'),
    path('razorpay_callback/<int:id>/', views.razorpay_callback, name='razorpay_callback'),
    path('success/<str:order_id>/',views.success,name='success'),
    path('failure/<int:id>/',views.failure,name='failure'),
    path('indiviudalcancel/<int:id>/<int:id2>/',views.indiviudalcancel,name='indiviudalcancel'),
    path('individual_return/<int:id>/<int:id2>/',views.individual_return,name='individual_return'),
    path('invoice_download/<int:id>',views.invoice_download,name='invoice_download'),
    # ===============================Admin==============================================
    path('admin_order_list/',views.admin_order_list,name='admin_order_list'),
    path('admin_order_details/<int:id>/',views.admin_order_details,name='admin_order_details'),
    path('change_order_status/<int:id>/',views.change_order_status,name='change_order_status'),
    path('admin_review/',views.admin_review,name='admin_review')

     
]