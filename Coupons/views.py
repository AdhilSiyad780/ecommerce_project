from django.shortcuts import render,redirect
from django.contrib import messages
from Coupons.models import coupons
from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.shortcuts import get_object_or_404




# Create your views here.


def list_coupons(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
        
    alpha = coupons.objects.all()
    context = {
        'coupons':alpha
    }
    return render(request,'admin/coupon_list.html',context)

def create_coupons(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    error = ''
    if request.method=='POST':
        code=request.POST.get('code')
        discount = request.POST.get('discount')
        min_purchase =request.POST.get('MIN-purchase')
        valid_from = request.POST.get('validfrom')
        valid_to = request.POST.get('validto')
        limit = request.POST.get('limit')
        if any(not item for item in [code,discount,min_purchase,valid_from,valid_to,limit]):
            error='not field can be empty'
        try:
            valid_from_date = datetime.strptime(valid_from,"%Y-%m-%d")
            valid_to_date = datetime.strptime(valid_to,"%Y-%m-%d")
            if valid_from_date > valid_to_date:
                error='Date should be correct'
        except ValueError:
            error = 'Invalid date format'
       
        if not (any(char.isdigit()) for char in code) and (any(char.isalpha() for char in code)):
            error='code should be combination  of both number and charactar'
        if not discount.isdigit:
            error = 'discount should be a number'
        if not discount.isdigit():
            error = 'the discount should be less than 50'
        try:
            if int(limit) <= 0:
                error = 'limit should be greater than 1'
        except ValueError:
            error='limit is empty'
        try:
            newdiscount = Decimal(discount)
        except InvalidOperation:
            error='discount cant be empty'
        
        if error:
            
            messages.error(request,error)
            return redirect('list_coupons')
        
        coupons.objects.create(code=code,discount_value=newdiscount,min_purchase_amount=min_purchase,valid_from=valid_from,valid_to=valid_to,usage_limit=limit)
        return redirect('list_coupons')
        
        
    return render(request,'admin/coupon_list.html')

def edit_coupon(request,id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    error=None
    coupon=get_object_or_404(coupons,id=id)
    if request.method == 'POST':
        code=request.POST.get('code')
        discount = request.POST.get('discount')
        min_purchase =request.POST.get('MIN-purchase')
        valid_from = request.POST.get('validfrom')
        valid_to = request.POST.get('validto')
        limit = request.POST.get('limit')
        if not (any(char.isdigit() for char in code) and any(char.isalpha() for char in code)):
            error='not field can be empty'
        try:
            valid_from_date = datetime.strptime(valid_from,"%Y-%m-%d")
            valid_to_date = datetime.strptime(valid_to,"%Y-%m-%d")
            if valid_from_date > valid_to_date:
                error='Date should be correct'
        except ValueError:
            error = 'Invalid date format'
       
        if not (any(char.isdigit()) for char in code) and (any(char.isalpha() for char in code)):
            error='code should be combination  of both number and charactar'
        if not discount.isdigit() or int(discount) > 50:
            error = 'The discount should be a number and less than 50'

        try:
            limit_int = int(limit)
            if limit_int <= 0:
                error = 'Limit should be greater than 1'
        except ValueError:
               error = 'Limit should be a valid number'

        try:
            newdiscount = Decimal(discount)
        except InvalidOperation:
            error='discount cant be empty'
        
        if error:
            
            messages.error(request,error)
            return redirect('edit_coupon',id)
        coupon.code=code
        coupon.discount_value=newdiscount
        coupon.min_purchase_amount=min_purchase
        coupon.valid_from=valid_from_date
        coupon.valid_to=valid_to_date
        coupon.usage_limit=limit
        coupon.save()
        return redirect('list_coupons')



    context = {
        'coupon':coupon,
    }
    return render(request,'admin/coupon_edit.html',context)

def remove_coupon(request):
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
        messages.success(request,'removed coupon successfully')
    else:
        messages.error(request,'No coupon applied')

    return redirect('checkout')
            
