from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from .models import admin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import sweetify
from django.db.models import Sum, Count, F,FloatField
from order.models import AlOrder,AlOrderItem
from django.db import models








# Create your views here.

def admin_login(request):
    error=None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        
        user = authenticate(request,username=username,password=password)
        print(user)
        if not user:
            error='invalid username or password'
        if user is not None and user.is_staff:
            login(request,user)
            return redirect('admin_home')
        return render(request,'admin/admin-login.html',{'error':error})
         
    return render(request,'admin/admin-login.html')

# ====================================================================================================================
def admin_logout(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    logout(request)
    return redirect('login')
# ====================================================================================================================
def admin_home(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    total_orders = AlOrder.objects.count()
    total_users = User.objects.filter(is_active=True).count()
    total_sales = AlOrder.objects.aggregate(total=Sum('total_price'))['total'] or 0
    total_discount = AlOrder.objects.filter(coupon__isnull=False).aggregate(
        total_discount=Sum(
            F('total_price') * F('coupon__discount_value')/100,
            output_field=FloatField()
        )
    )['total_discount'] or 0
    max_selling_product = AlOrderItem.objects.values('product__name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity').first()

    

    context = {
        "total_orders": total_orders,
        "total_sales": total_sales,
        "total_discount": total_discount,
        "max_selling_product": max_selling_product,
        "total_users": total_users,
    }
    return render(request,'admin/indexadmin.html',context)
# =================================================================================================================
def user_list(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    
    user = User.objects.order_by('id')


    return render(request,'admin/page-user.html',{'user': user})

def user_status(request,id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    alpha = get_object_or_404(User,pk=id)
    if alpha.is_active==True:
        User.objects.filter(id=alpha.id).update(is_active = False)
    else:
         User.objects.filter(id=alpha.id).update(is_active = True)

    return redirect('user_list')