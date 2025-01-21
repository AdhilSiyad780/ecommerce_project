from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from products.models import Products,SizeVariant
from .models import Cart,Cartitems
from django.db.models import F, Case, When, Value, FloatField, Sum
from userprofile.models import useraddress
from django.http import JsonResponse
from django.contrib import messages
from Coupons.models import coupons
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import F, Sum
from django.contrib import messages
from .models import Cartitems, Cart
from django.shortcuts import render, redirect
from django.db.models import F, Sum
from django.http import JsonResponse
from .models import Cart, Cartitems  
from .models import Cart, Cartitems, DeliveryCharge
from django.contrib.auth.decorators import login_required


@login_required(login_url='login_user')
def cart(request):
    if not request.user.is_authenticated:
        return redirect('login_user')

    # Initialize total_items early to ensure it's always defined
    total_items = []

    # Fetch the cart for the logged-in user
    gama = Cart.objects.filter(user=request.user).first()
    
    # If no cart exists, set items to an empty list
    if not gama:

        items = []
        cart_total = 0  # No cart means no total
    else:
        try:
            # Get the cart items
            items = Cartitems.objects.filter(cart=gama,product__is_active=True,product__catagory__is_active=True)

            # Initialize total_items here as well to ensure it's always available
            total_items = []  # It's safe to re-initialize it
        except Exception as e:  # Capture the exception correctly
            print(e)
            items = []
            total_items = []  # Ensure total_items is reset in case of an error
        
        # Calculate the cart total
        cart_total = cart_total_cal(request)
        # Populate total_items with cart item details
        for item in items:
            size_variant = item.product.size_variant.filter(size=item.size).first()
            stock = size_variant.stock if size_variant else 0
            total_items.append({'item': item, 'stock': stock})

    # Render the cart page with items and total
    return render(request, 'cart.html', {'items': total_items, 
                                         'carttotal': cart_total,
                                         'shipping': cart_total + 150})

@login_required(login_url='login_user')
def addcart(request, id, size=None):

    if not request.user.is_authenticated:
        return redirect('login_user')

    alpha = get_object_or_404(Products, id=id)
    user = request.user
    size_variant = alpha.size_variant.filter(size=size).first()
    stock = size_variant.stock if size_variant else 0  # Handle size_variant being None
    
    quantity = int(request.POST.get('quantity', 1))
    
    if stock == 0:
        messages.error(request, 'Product is out of stock')
        return redirect('product_details', id)
   
    if quantity > stock:
        messages.warning(request, f'Only {stock} items available. Adjusted to stock limit.')
        quantity = stock

    cart, created = Cart.objects.get_or_create(user=user)
    
    cart_item, created = Cartitems.objects.get_or_create(
        cart=cart,
        product=alpha,
        size=size,
        defaults={'quantity': quantity}
    )

    
    if cart_item.quantity<5:
        if not created: 
            if cart_item.quantity + quantity > stock:
                cart_item.quantity = stock
                messages.error(request, 'max stock reached')
                return redirect('product_details', id)
            else:
                cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, 'Product quantity updated in the cart')
            return redirect('product_details', id)

    
        else:
            messages.success(request, 'Product added to the cart successfully')
            return redirect('product_details', id)
    else:
        messages.error(request,'only 5 product per product')


    return redirect('product_details', id)


@login_required(login_url='login_user')
def update_cart(request, id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    if request.method == 'POST':
        action = request.POST.get('action')
        cart_item = get_object_or_404(Cartitems, id=id)
        
        # Get stock for the specific size variant
        size_variant = cart_item.product.size_variant
        thestock = size_variant.filter(size=cart_item.size).first()
        stock = thestock.stock if thestock else 0
        
        # Validation for max quantity
    
        if cart_item.quantity == 5 and action == 'increase':
            return JsonResponse({
                'status': 'error', 
                'message': 'Only 5 items allowed',
                'current_quantity': cart_item.quantity
            })
        
        # Validation for stock limit
        if cart_item.quantity >= stock and action == 'increase':
            messages.error(request, 'You have ordered the full stock')
            return JsonResponse({
                'status': 'error', 
                'message': 'Full stock reached',
                'current_quantity': cart_item.quantity
            })

        # Update quantity
        if action == 'increase':
            if cart_item.quantity < stock:
                cart_item.quantity += 1
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1

        cart_item.save()
        
        # Recalculate cart total
        
        cart_total = cart_total_cal(request)
        print(cart_item.quantity)
        return JsonResponse({
            'status': 'success',
            'quantity': cart_item.quantity,
            'item_total': float(cart_item.product.price) * cart_item.quantity,
            'carttotal': cart_total,
            'shipping': cart_total + 150
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def cart_total_cal(request):
    cart = Cart.objects.filter(user=request.user).first()
    items = Cartitems.objects.filter(cart=cart,product__is_active=True,product__catagory__is_active=True)
    cart_total = items.annotate(
    # Calculate the effective price based on product and category offers
    effective_price=Case(
        When(
            product__catagory__offer__gt=0,  # Apply category offer if it exists
            then=F('product__offer') * (1 - F('product__catagory__offer') / 100)  # Reduce the product offer by category discount
        ),
        default=F('product__offer'),  # Otherwise, use the product offer price
        output_field=FloatField(),
    ),
    # Calculate the total for each item
    item_total=F('effective_price') * F('quantity')
    ).aggregate(
    total=Sum('item_total')
    )['total'] or 0  # Default to 0 if no items

    return cart_total




@login_required(login_url='login_user')
def deletecart(request,id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    alpha = get_object_or_404(Cartitems,id=id)
    Cartitems.objects.filter(id=alpha.id).delete()
    return redirect('cart')

from django.http import JsonResponse




@login_required(login_url='login_user')
def chectout(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    
    formdata = request.session.get('form-data',{})
    
    cart = Cart.objects.filter(user=request.user).first()
    discount=0
    if not cart:
        messages.error(request,'Your Cart is Empty')
        return redirect('cart')
    cart_items = Cartitems.objects.filter(cart=cart,product__is_active=True,product__catagory__is_active=True)
    for item in cart_items:
        stock = item.product.size_variant.filter(size=item.size).first()
        name = item.product.name
        if stock and stock.stock< item.quantity:
            messages.error(request,f'The product {name} does not have this much stock or it is out of stock')
            return redirect('cart')
    # Fetch cart items
    items = Cartitems.objects.filter(cart=cart.id,product__is_active=True,product__catagory__is_active=True)
    sub_total = cart_total = items.annotate(
        item_total=F('product__price') * F('quantity')
     ).aggregate(total=Sum('item_total'))['total'] or 0

    # Fetch user addresses
    address = useraddress.objects.filter(user=request.user)[:3]

    # Calculate the total

    cart_total = cart_total_cal(request)
    print('cart total',cart_total)
    cart_total =Decimal(cart_total)
    total_discount = sub_total-cart_total
    applied_coupon = request.session.get('applied_coupon', None)
    coupon = None
    if applied_coupon:
        coupon = get_object_or_404(coupons,id=applied_coupon['id'])
        print('========-=================-==================================')
        if coupon:
            if float(coupon.min_purchase_amount)>(cart_total+150):
                del request.session['applied_coupon']
                print('=====================           ====================        ===================         ===================')
                messages.error(request, 'Please add more items to the apply this coupon')
                return redirect('checkout')
    
    
    
    if cart_total==0:
        return redirect('cart')
    discount = 0
    if applied_coupon:
        print('=============================================================================')
        cart_total=Decimal(cart_total)
        discount = cart_total * (Decimal(applied_coupon['discount_value']) / Decimal(100))
        cart_total-=discount
        print('after discount',cart_total)
        total_discount+=discount
        
    passcoupon=coupons.objects.filter(usage_limit__gt=0) 

    


    # Context for the template
    context = {
        'items': items,
        'address': address,
        'cart_item': cart_total+150,
        'sub_total':cart_total,
        'coupons':passcoupon,
        'applied_coupon':applied_coupon['code'] if applied_coupon else '',
        'sub_total':sub_total,
        'total_discount':total_discount,
        'coupon_discount':discount,
        'formdata':formdata
    }

    return render(request, 'checkout.html', context)


