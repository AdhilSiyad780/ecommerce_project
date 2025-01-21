from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from .models import admin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import sweetify
from django.db.models import Sum, Count, F,FloatField
from order.models import AlOrder,AlOrderItem
from django.db import models
from django.db.models.functions import ExtractYear,ExtractMonth
from datetime import datetime
import json
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import CharField
from django.utils import timezone



# Create your views here.
def admin_login(request):
    if request.user.is_staff==True and  request.user.is_authenticated:
        return redirect('admin_home') 
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
@login_required(login_url='adminlogin')
def admin_logout(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    logout(request)
    return redirect('adminlogin')
# ====================================================================================================================
@login_required(login_url='adminlogin')
def admin_home(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
        
    total_orders = AlOrder.objects.count()
    total_users = User.objects.filter(is_active=True).count()
    total_sales = AlOrder.objects.filter(status='delivered').aggregate(total=Sum('real_price'))['total'] or 0
    total_discount = AlOrder.objects.filter(status='delivered',coupon__isnull=False).aggregate(
        total_discount=Sum(
            F('real_price') * F('coupon__discount_value')/100,
            output_field=FloatField()
        )
    )['total_discount'] or 0
    
    max_selling_product = AlOrderItem.objects.values('product__name','product__image1').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity').first()
    
    products = AlOrderItem.objects.values('product__name','product__image1').annotate(
        total_quantity = Sum('quantity')
    ).order_by('-total_quantity')[:5]

    # Get current year
    categories = AlOrderItem.objects.values('product__catagory__name','product__catagory__image').annotate(
        total = Sum('quantity')
    ).order_by('-total')[:3]


    monthly_data = {}
    for year in range(2020, datetime.now().year + 1):
        monthly_data[year] = {}
        for month in range(1, 13):
            sales = AlOrder.objects.filter(
                status='delivered',
                created_at__year=year,
                created_at__month=month,
                
            ).aggregate(
                total=Sum('real_price')
            )['total'] or 0
            monthly_data[year][month] = float(sales)
    
    # Prepare yearly data
    yearly_data = {}
    for year in range(2020, datetime.now().year + 1):
        sales = AlOrder.objects.filter(
            status='delivered',
            created_at__year=year
        ).aggregate(
            total=Sum('real_price')
        )['total'] or 0
        yearly_data[year] = float(sales)
    
    
    context = {
        "total_orders": total_orders,
        "total_sales": total_sales,
        "total_discount": total_discount,
        "max_selling_product": max_selling_product,
        "products":products,
        "categories":categories,
        "total_users": total_users,
        'monthly_data': monthly_data,
        'yearly_data': yearly_data,
        'available_years': list(range(2020, datetime.now().year + 1)),
        'current_year': datetime.now().year,
    }
    
    return render(request, 'admin/indexadmin.html', context)
# =================================================================================================================
@login_required(login_url='adminlogin')
def user_list(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    
    user = User.objects.order_by('id').all()
    search_query = request.GET.get('search','').strip()
    if search_query:
        user = user.filter(
            Q(id__icontains=search_query)|
            Q(username__icontains=search_query)|
            Q(email__icontains=search_query)
        )
    paginator = Paginator(user, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request, 'admin/page-user.html', {'items': page_obj, 'search_query': search_query})

@login_required(login_url='adminlogin')
def user_status(request,id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    alpha = get_object_or_404(User,pk=id)
    if alpha.is_active==True:
        User.objects.filter(id=alpha.id).update(is_active = False)
    else:
         User.objects.filter(id=alpha.id).update(is_active = True)

    return redirect('user_list')


def sales_statistics(request):
    # Fetch total sales by month
    sales_data = (
        AlOrderItem.objects
        .annotate(month=ExtractMonth('created_at'))  # Extract month from the order date
        .values('month')  # Group by month
        .annotate(total_sales=Sum('price'))  # Sum sales for each month
        .order_by('month')  # Sort by month
    )

    # Prepare data for the graph
    months = [datetime(2025, item['month'], 1).strftime('%B') for item in sales_data]  # Convert month number to name
    sales = [item['total_sales'] for item in sales_data]

    # Pass the data to the template
    return render(request, 'sales_statistics.html', {
        'months': months,
        'sales': sales,
    })
