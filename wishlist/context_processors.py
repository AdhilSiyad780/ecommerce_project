from wishlist.models import Wishlist,Wishlistitems
from cart.models import Cart,Cartitems

def cart_and_wishlist_counts(request):
    if request.user.is_authenticated:
        cart_ = Cart.objects.filter(user=request.user).first()
        wishlist_ = Wishlist.objects.filter(user=request.user).first()
        cart_count = Cartitems.objects.filter(cart=cart_).count()
        wishlist_count=Wishlistitems.objects.filter(wishlist=wishlist_).count()
        
    else:
        cart_count = 0
        wishlist_count = 0
    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }
