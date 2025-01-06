from django.urls import path
from . import views

urlpatterns = [
    path('transaction_list/',views.transaction_list,name='transaction_list'),
    path('download-sales-excel/', views.download_sales_excel, name='download_sales_excel'),
    path('download_sales_pdf/',views.download_sales_pdf,name='download_sales_pdf'),
    

    

]