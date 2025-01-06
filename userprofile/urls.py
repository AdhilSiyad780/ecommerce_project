from django.urls import path
from . import views

urlpatterns = [
    
    path('userprofile/',views.userprofile,name='userprofile'),
    path('updateprofile/',views.updateprofile,name='updateprofile'),
    path('add_address/',views.add_address,name='add_address'),
    path('editaddress/<int:id>',views.editaddress,name='editaddress'),
    path('delete_address/<int:id>',views.delete_address,name='delete_address'),
    path('changepassword/',views.changepassword,name='changepassword'),

]