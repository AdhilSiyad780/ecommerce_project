from django.shortcuts import render,redirect
from wishlist.models import Wishlist,Wishlistitems
from django.shortcuts import get_object_or_404
from products.models import Products,SizeVariant
from django.contrib import messages
from django.http import JsonResponse
from cart.models import Cart
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
    alpha=get_object_or_404(Wishlistitems,id=id)
    addcart(request,alpha.product.id,alpha.size)

    return redirect('wishlist')



# =======================================================================================
