from django.urls import path
from auth_user import views

urlpatterns = [
    path('signup/',views.signup,name='signup'),
    path('login_user',views.login_user,name='login_user'),
    path('verify_otp/<str:email>/',views.verify_otp,name='verify_otp'),
    path('resend_otp/<str:email>/',views.resend_otp,name='resend_otp'),
    path('logout_user/',views.logout_user,name='logout_user'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('verify_reset_otp/<str:email>/',views.verify_reset_otp,name='verify_reset_otp'),
    path('verify_password/<str:email>/',views.verify_password,name='verify_password'),
    path('',views.home,name ='index'),
    
    
]