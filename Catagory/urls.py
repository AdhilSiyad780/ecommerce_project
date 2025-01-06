from django.urls import path
from Catagory import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
   path('catagory_list/',views.catagory_list,name='catagory_list'),
   path('create_catagory/',views.create_catagory,name='create_catagory'),
   path('edit_catagory/<int:id>',views.edit_catagory,name = 'edit_catagory'),
   path('unlist_catagory/<int:id>',views.unlist_catagory,name='unlist_catagory'),
   #================================================================================================================
 
]


