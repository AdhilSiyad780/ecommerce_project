from django.urls import path
from admin_auth import views

urlpatterns = [
    path('adminlogin/',views.admin_login,name='adminlogin'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    path('admin_home/',views.admin_home,name='admin_home'),
    path('user_list/',views.user_list,name='user_list'),
    path('user_status/<int:id>/',views.user_status,name='user_status'),
    path('sales/', views.sales_statistics, name='sales_statistics'),

    

]
