from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from products.models import Products,SizeVariant
from .models import Cart,Cartitems
from django.db.models import F,Sum
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
from .models import Cart, Cartitems  # Import your models properly
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
            items = Cartitems.objects.filter(cart=gama)

            # Initialize total_items here as well to ensure it's always available
            total_items = []  # It's safe to re-initialize it
        except Exception as e:  # Capture the exception correctly
            print(e)
            items = []
            total_items = []  # Ensure total_items is reset in case of an error
        
        # Calculate the cart total
        cart_total = items.annotate(
            item_total=F('product__offer') * F('quantity')
        ).aggregate(total=Sum('item_total'))['total'] or 0  # Default to 0 if total is None
        
        # Populate total_items with cart item details
        for item in items:
            size_variant = item.product.size_variant.filter(size=item.size).first()
            stock = size_variant.stock if size_variant else 0
            total_items.append({'item': item, 'stock': stock})

    # Render the cart page with items and total
    return render(request, 'cart.html', {'items': total_items, 
                                         'carttotal': cart_total,
                                         'shipping': cart_total + 150})



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
    
    if not created: 
        if cart_item.quantity < 5:
            cart_item.quantity+=1
            cart_item.save()
            messages.success(request, 'Product quantity updated in the cart')
    
    else:
        messages.success(request, 'Product added to the cart successfully')

    return redirect('product_details', id)



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
    items = Cartitems.objects.filter(cart=cart)
    cart_total = items.annotate(
        item_total=F('product__offer') * F('quantity')
    ).aggregate(total=Sum('item_total'))['total'] or 0 
    return cart_total





def deletecart(request,id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    alpha = get_object_or_404(Cartitems,id=id)
    Cartitems.objects.filter(id=alpha.id).delete()
    return redirect('cart')

from django.http import JsonResponse





def chectout(request):
    if not request.user.is_authenticated:
        return redirect('login_user')

    cart = Cart.objects.filter(user=request.user).first()

    if not cart:
        messages.error(request,'Cart is Empty')
        return redirect('cart')
    cart_items = Cartitems.objects.filter(cart=cart)
    for item in cart_items:
        stock = item.product.size_variant.filter(size=item.size).first()
        name = item.product.name
        if stock and stock.stock< item.quantity:
            messages.error(request,f'The product {name} does not have this much stock or it is out of stock')
            return redirect('cart')
    # Fetch cart items
    items = Cartitems.objects.filter(cart=cart.id)

    # Fetch user addresses
    address = useraddress.objects.filter(user=request.user)[:3]

    # Calculate the total
    cart_total = items.annotate(
        item_total=F('product__offer') * F('quantity')
    ).aggregate(total=Sum('item_total'))['total'] or 0  # Defa₹ult to 0 if no items
    applied_coupon=request.session.get('applied_coupon',False)

    
    if cart_total==0:
        return redirect('cart')
    if applied_coupon:
        print('=============================================================================')

        discount = cart_total * (Decimal(applied_coupon['discount_value']) / Decimal(100))
        cart_total-=discount
    try:
        Coupons = coupons.objects.all()
    except Exception as e:
        Coupons=None
        print(f'error : {e}')

    # Context for the template
    context = {
        'items': items,
        'address': address,
        'cart_item': cart_total+150,
        'sub_total':cart_total,
        'coupons':Coupons,
        'applied_coupon':applied_coupon['code'] if applied_coupon else ''
    }

    return render(request, 'checkout.html', context)





