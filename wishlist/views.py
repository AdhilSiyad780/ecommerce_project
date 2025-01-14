from django.shortcuts import render,redirect
from wishlist.models import Wishlist,Wishlistitems
from django.shortcuts import get_object_or_404
from products.models import Products,SizeVariant
from django.contrib import messages
from django.http import JsonResponse
from cart.models import Cart,Cartitems
from cart.views import addcart

# Create your views here.

def wishlist(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    alpha = Wishlist.objects.filter(user=request.user).first()
        
    items = Wishlistitems.objects.filter(wishlist=alpha)
    total_items=[]
    for item in items:
        size_variant = item.product.size_variant.filter(size=item.size).first()
        stock = size_variant.stock if size_variant else 0
        total_items.append({'item':item,'stock':stock})
    print(total_items)
    context = {
    'items':total_items,
        }
    
    return render(request,'wishlist.html',context)


def add_wishlist(request,id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    product = get_object_or_404(Products,id=id)
    user = request.user
    
    wishlist,created = Wishlist.objects.get_or_create(user=user)
    sample = SizeVariant.objects.filter(product=product).first()
    if not sample:
        return redirect('display_products')
    
    
   
    items = Wishlistitems.objects.filter(wishlist=wishlist,product=product.id,size=sample.size).exists()
    if  items:
        messages.info(request, f"{product.name} (Size: {sample.size}) is already in your wishlist.")
    else:
        Wishlistitems.objects.create(wishlist=wishlist,product=product,size=sample.size)
    # ===================================================================================================================

    alpha = Wishlist.objects.filter(user=request.user).first()
        
    items = Wishlistitems.objects.filter(wishlist=alpha)
    total_items=[]
    for item in items:
        size_variant = item.product.size_variant.filter(size=item.size).first()
        stock = size_variant.stock if size_variant else 0
        total_items.append({'item':item,'stock':stock})
    print(total_items)
    context = {
    'items':total_items,
    }
    

    return render(request,'wishlist.html',context)

def add_wishlist_from_product_details(request,id,size):
    if not request.user.is_authenticated:
        return redirect('login_user')
    product =get_object_or_404(Products,id=id)
    wishlist,created = Wishlist.objects.get_or_create(user=request.user)
    items = Wishlistitems.objects.filter(wishlist=wishlist,product=product.id,size=size).exists()
    if items:
        messages.error(request,f'{product.name} with {size} size already exists in your wishlist')
    else:
        Wishlistitems.objects.create(wishlist=wishlist,product=product,size=size)
    
        messages.success(request,'Product added to wishlist successfully')

    return redirect('product_details',id)

def delete_wishlist(request,id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    Wishlistitems.objects.filter(id=id).delete()
    return redirect('wishlist')

def wishlist_to_cart(request,id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    wishlistitem=get_object_or_404(Wishlistitems,id=id)
    # addcart(request,alpha.product.id,alpha.size)
    alpha = wishlistitem.product
    user = request.user
    size_variant = alpha.size_variant.filter(size=wishlistitem.size).first()
    stock = size_variant.stock if size_variant else 0 
    quantity = int(request.POST.get('quantity', 1))
    if stock == 0:
        return redirect('wishlist')
   
    if quantity > stock:
        messages.warning(request, f'Only {stock} items available. Adjusted to stock limit.')
        quantity = stock
    cart, created = Cart.objects.get_or_create(user=user)
    
    cart_item, created = Cartitems.objects.get_or_create(
        cart=cart,
        product=alpha,
        size=wishlistitem.size,
        defaults={'quantity': quantity}
    )
    
    if cart_item.quantity<5:
        if not created: 
            if cart_item.quantity + quantity > stock:
                cart_item.quantity = stock
                messages.error(request,'maximum stock reached')
                return redirect('wishlist')
            else:
                cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, 'Product quantity updated in the cart')
            return redirect('wishlist')

    
        else:
            messages.success(request, 'Product added to the cart successfully')
            return redirect('wishlist')
    else:
        messages.error(request,'Can only add 5 quantity')
    return redirect('wishlist')



# =======================================================================================
