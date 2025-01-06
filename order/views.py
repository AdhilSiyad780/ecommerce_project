from django.db.models import F,Sum
from django.shortcuts import   get_object_or_404
from Coupons.models import coupons
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db.models import F, Sum
from cart.models import Cart, Cartitems
from order.models import AlOrder,AlOrderItem
from userprofile.models import useraddress
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction
from products.models import Products,Review_ration
from django.utils.timezone import now
from decimal import Decimal
from cart.views import cart_total_cal,chectout
import razorpay
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from Coupons.models import coupons,wallet
from transaction.models import transactions
from django.db.models import Q
from django.core.paginator import Paginator








def placeorder(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    if request.method == 'POST':
        address_id = request.POST.get('selected_address_id')
        payment_type = request.POST.get('payment_type')
        print(payment_type)
        print(address_id,'----------------------------------------------------------')

        if not address_id:
            messages.error(request, 'Please select an address.')
            return redirect('checkout')
        address = useraddress.objects.get(user=request.user,id=address_id)


        gama = Cart.objects.filter(user=request.user).first()
        if not gama:
            messages.error(request, 'Your cart is empty. Please add items before proceeding.')
            return redirect('checkout')

        items = Cartitems.objects.filter(cart=gama)
        coupon_obj = None
        # Calculate the cart total
        cart_total =  items.annotate(
        item_total=F('product__offer') * F('quantity')
    ).aggregate(total=Sum('item_total'))['total'] or 0
        applied_coupon = request.session.get('applied_coupon', None)
        if applied_coupon:
            coupon_obj = coupons.objects.get(id=applied_coupon['id'])
            discount = cart_total * (Decimal(applied_coupon['discount_value']) / Decimal(100))
            cart_total -= discount

        # Get the selected shipping address
        shipping_address = useraddress.objects.filter(id=address_id, user=request.user).first()
        if not shipping_address:
            messages.error(request, 'Invalid address selection.')
            return redirect('checkout')

        if cart_total == 0:
            messages.error(request, 'No products have been added')
            return redirect('checkout')

        # Razorpay integration for online payment
        if payment_type == 'razorpay':
            try:
                # Initialize Razorpay client
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

                # Create Razorpay order
                razorpay_order = client.order.create({
                    'amount': int((cart_total + 150) * 100),  # Convert to paisa
                    'currency': 'INR',
                    'payment_capture': '1',  # Auto-capture payment
                })
                # Save order details locally
                request.session['razorpay_order_id'] = razorpay_order['id']
                request.session['address_selected'] = address_id

                print('2222222222222222222222222222222222222222')

                return render(request, 'payment_page.html', {
                    'razorpay_order_id': razorpay_order['id'],
                    'razorpay_key': settings.RAZORPAY_KEY_ID,
                    'amount': cart_total+150,
                    'user_email': request.user.email,
                    'user_contact': address_id,  
                })
            except Exception as e:
                messages.error(request, f"Error creating Razorpay order: {str(e)}")
                return redirect('checkout')
         
        elif payment_type == 'cash_on_delivery': 
            order = AlOrder.objects.create(
                user=request.user,
                address=shipping_address,
                payment_method=payment_type,
                total_price=cart_total+150,
                coupon = coupon_obj,
                status='pending',
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            # Deduct stock and clear the cart
            _finalize_order(request, items, order)
            return render(request, 'success.html', {'order': order})

        else:
            messages.error(request, 'Invalid payment method.')
            return redirect("checkout")

    return redirect('checkout')


def _finalize_order(request, items, order):
    """Helper function to finalize the order: deduct stock and clear cart."""
    try:
        with transaction.atomic():
            for item in items:
                product = item.product
                size_variant = product.size_variant.filter(size=item.size).first()
                if size_variant:
                    if size_variant.stock < item.quantity:
                        raise ValueError(f"Not enough stock for {product.name} - {size_variant.size}")
                    size_variant.stock -= item.quantity
                    size_variant.save()
                AlOrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price,
                    size_variant=size_variant,
                )
            # Clear cart
                Cart.objects.filter(user=request.user).delete()
                print('cart is deleted======================================================')
    except Exception as e:
        raise e


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def razorpay_callback(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    if request.method == 'POST':
        print('===============================sdgg===============asddgg==================')
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payload = request.POST
        razorpay_order_id = payload.get('razorpay_order_id')
        razorpay_payment_id = payload.get('razorpay_payment_id')
        razorpay_signature = payload.get('razorpay_signature')

        try:
            # Verify the Razorpay signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            # Update order status to success
            print('bla=================================balakldlka')
            print(razorpay_order_id)
            
            gama = Cart.objects.filter(user=request.user).first()

            items = Cartitems.objects.filter(cart=gama)
            cart_total = cart_total_cal(request)
            applied_coupon = request.session.get('applied_coupon', None)
            coupon_obj=None
            if applied_coupon:
                coupon_obj = coupons.objects.get(id=applied_coupon['id'])
                discount = cart_total * (Decimal(applied_coupon['discount_value']) / Decimal(100))
                cart_total -= discount  # Replace with your cart total logic
            address_selected = request.session.get('address_selected')
            
            shipping_address = useraddress.objects.filter(id=address_selected, user=request.user).first()
            print(address_selected,shipping_address)
            if not shipping_address:
                messages.error(request,'a adress problem')
                return redirect('checkout')
            
            # Create the order only after successful payment
            order = AlOrder.objects.create(
                user=request.user,
                address=shipping_address,
                payment_method='razorpay',
                total_price=cart_total+150,
                razorpay_order_id=razorpay_order_id,
                coupon=coupon_obj,
                status='completed',  # Mark as completed
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            order = AlOrder.objects.get(razorpay_order_id=razorpay_order_id)
            order.status = 'completed'
            order.save()
            _finalize_order(request, items, order)
            print('-----3333333333333333333333333333333333333333333333333333333333333333')
            return redirect('success', order_id=order.id)

        except Exception as e:
            print(e)
            return render(request, 'failure.html', {'error': str(e)})

    return redirect('checkout')
def success(request,order_id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    order = AlOrder.objects.get(id=order_id)
    return render(request,'success.html',{'order':order})
def failure(request):

    return render(request,'failure.html')


def apply_coupon(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    if request.method=='POST':
        coupon_code=request.POST.get('coupon_code')
        total = cart_total_cal(request)
        if not coupon_code:
            messages.error(request,'Enter a coupon code')
            return redirect('checkout') 
        try:
            coupon = coupons.objects.get(code=coupon_code,active=True,valid_to__gte=now(),valid_from__lte=now())

            if coupon:
                if coupon.min_purchase_amount > Decimal(total):
                    print('=================================8798==========================')
                    messages.error(request,'Add more item for applying this coupon')
                    return redirect('checkout')
                request.session['applied_coupon']={
                    'id':coupon.id,
                'code': coupon.code,
                'discount_value':coupon.discount_value,
                }
                messages.success(request,'coupon applied sucessfully')
        except coupons.DoesNotExist:
            messages.error(request,'The coupon is expired or invalid')
        return redirect('checkout')

    return redirect('checkout')

def orderlist(request):
    details = AlOrder.objects.filter(user=request.user).all()
    context = {
        'orderdetails':details,
        'active_tab': 'orders'
    }

    return render(request,'userprofile.html',context)

def orderdetails(request,id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    alpha = get_object_or_404(AlOrder,id=id)
    if alpha.total_price<200:
        print('=======================asdg=======asdf=========asdf')
        alpha.total_price=0
        alpha.save()
    sample = alpha.address
    context = {
        'order':alpha,
        'address':sample
    }
    print(sample)
    return render(request,'orderdetails.html',context)




def  cancel_order(request, id):
    # Fetch the order
    if not request.user.is_authenticated:
        return redirect('login_user')
    order = get_object_or_404(AlOrder, id=id, user=request.user)

    # Check if the order is still pending
    if order.status == 'pending' or order.status == 'completed':
        # Use a transaction to ensure consistency in stock updates
        try:
            with transaction.atomic():
                # Loop through all order items and revert the stock changes
                for item in order.items.all():
                    size_variant = item.size_variant
                    if size_variant:
                        # Increase the stock by the quantity in the order
                        size_variant.stock += item.quantity
                        size_variant.save()
                if order.status=='pending':
                    thewallet, created = wallet.objects.get_or_create(user=request.user, defaults={'balance': Decimal('0')})
                    thewallet.balance += order.total_price
                    thewallet.save()
                    transactions.objects.create(user=request.user,order=order,payment_type='razorpay',amount=order.total_price,
                                        status='Canceled')
                # Update the order status to 'canceled'
                order.status = 'canceled'
                order.save()
                # Delete a specific session key
               
 
            messages.success(request, 'Your order has been successfully canceled, and stock has been updated.')
        except Exception as e:
            messages.error(request, f'Error occurred while canceling the order: {str(e)}')
    else:
        messages.error(request, 'You cannot cancel this order as it is no longer pending.')

    # Redirect back to the order details page
    return redirect('orderdetails',id=id)

# ============================================admin=======================admin===================================================

def admin_order_list(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    search_query = request.GET.get('search', '').strip()
    alpha = AlOrder.objects.all()
    if search_query:
        alpha = alpha.filter(
            Q(id__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    paginator = Paginator(alpha, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    
    context = {
        'items': page_obj,
        'search_query': search_query
    }
    return render(request,'admin/orders_list.html',context)

def admin_order_details(request,id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    try:
        alpha = get_object_or_404(AlOrder,id=id)
    except AlOrder.DoesNotExist:
        # return JsonResponse({'error':'does not exists'},status=400)
        return render(request,'admin/order_edit.html',{'item':alpha})
    return render(request,'admin/order_edit.html',{'item':alpha})

def indiviudalcancel(request,id,id2):
    if not request.user.is_authenticated:
        return redirect('login_user')
    print('===========================================')
    order = get_object_or_404(AlOrder,id=id)
    item = get_object_or_404(AlOrderItem,id=id2)
    items = AlOrderItem.objects.filter(order=order).all()
   
    if order.status == 'completed' :
        cart = items.annotate(
        item_total=F('product__offer') * F('quantity')
         ).aggregate(total=Sum('item_total'))['total'] or 0
        cart_total=cart+150
        if order.coupon:
            discount = cart_total * (Decimal(order.coupon.discount_value) / Decimal(100))
            print(f' discount: {discount}')
       
            total_quantity = AlOrderItem.objects.filter(order=order).aggregate(Sum('quantity'))['quantity__sum']
            print(f'total_quantity{total_quantity}')
            single = discount/total_quantity
            print(f'single{single}')
            reductable_amount = item.product.offer*item.quantity-item.quantity*single
            print(f'reductable_amount{reductable_amount}')

            
            
            size_variant = item.size_variant
            if size_variant:
                        # Increase the stock by the quantity in the order
                size_variant.stock += item.quantity
                item.quantity=0
                size_variant.save()
                item.save()
            
            thewallet, created = wallet.objects.get_or_create(user=request.user, defaults={'balance': Decimal('0')})
            thewallet.balance += reductable_amount
            thewallet.save()
            transactions.objects.create(user=request.user,order=order,payment_type='razorpay',amount=reductable_amount,
                                        status='Canceled')
            order.total_price -= reductable_amount
            order.save()
        else:
            reductable_amount=item.product.offer*item.quantity
            thewallet, created = wallet.objects.get_or_create(user=request.user, defaults={'balance': Decimal('0')})
            thewallet.balance += reductable_amount
            thewallet.save()
            transactions.objects.create(user=request.user,order=order,payment_type='razorpay',amount=reductable_amount,
                                        status='Canceled')
            size_variant = item.size_variant
            if size_variant:
                        # Increase the stock by the quantity in the order
                size_variant.stock += item.quantity
                item.quantity=0
                size_variant.save()
                item.save()
            print('=============================================================')
            order.total_price-=reductable_amount
            
        
    if order.status == 'pending':
        if order.coupon:
            cart = items.annotate(
        item_total=F('product__offer') * F('quantity')
         ).aggregate(total=Sum('item_total'))['total'] or 0
            cart_total=cart+150
            discount = cart_total * (Decimal(order.coupon.discount_value) / Decimal(100))
            print(f' discount: {discount}')
       
            total_quantity = AlOrderItem.objects.filter(order=order).aggregate(Sum('quantity'))['quantity__sum']
            print(f'total_quantity{total_quantity}')
            single = discount/total_quantity
            print(f'single{single}')
            reductable_amount = item.product.offer*item.quantity-item.quantity*single
            print(f'reductable_amount{reductable_amount}')
            order.total_price -= reductable_amount
            size_variant = item.size_variant
            if size_variant:
                        # Increase the stock by the quantity in the order
                size_variant.stock += item.quantity
                item.quantity=0
                size_variant.save()
                item.save()
        else:
            size_variant = item.size_variant
            if size_variant:
                        # Increase the stock by the quantity in the order
                size_variant.stock += item.quantity
                item.quantity=0
                size_variant.save()
                item.save()
            order.total_price-=item.product.offer
             

    if order.total_price<150 and order.status == 'completed':
        thewallet, created = wallet.objects.get_or_create(user=request.user, defaults={'balance': Decimal('0')})
        thewallet.balance +=14
        thewallet.save()
        order.total_price=0
    if order.total_price<150:
        order.total_price=0
    
    if items.filter(status='pending').count()==0:
        order.status='cancelled'
    order.save()
    item.status='cancelled'
    item.save()

    return redirect('orderdetails',id=order.id)

def individual_return(request,id,id2):
    if not request.user.is_authenticated:
        return redirect('login_user')
    print('===========================================')
    order = get_object_or_404(AlOrder,id=id)
    item = get_object_or_404(AlOrderItem,id=id2)
    items = AlOrderItem.objects.filter(order=order).all()
    cart = items.annotate(
        item_total=F('product__offer') * F('quantity')
         ).aggregate(total=Sum('item_total'))['total'] or 0
    cart_total=cart+150
    if order.coupon:
        discount = cart_total * (Decimal(order.coupon.discount_value) / Decimal(100))
        print(f' discount: {discount}')
       
        total_quantity = AlOrderItem.objects.filter(order=order).aggregate(Sum('quantity'))['quantity__sum']
        print(f'total_quantity{total_quantity}')
        single = discount/total_quantity
        print(f'single{single}')
        reductable_amount = item.product.offer*item.quantity-item.quantity*single
        print(f'reductable_amount{reductable_amount}')

        
            
        size_variant = item.size_variant
        if size_variant:
                        # Increase the stock by the quantity in the order
            size_variant.stock += item.quantity
            item.quantity=0
            size_variant.save()
            item.status='returned'
            item.save()
            
        thewallet, created = wallet.objects.get_or_create(user=request.user, defaults={'balance': Decimal('0')})
        thewallet.balance += reductable_amount
        thewallet.save()
        transactions.objects.create(user=request.user,order=order,payment_type='razorpay',amount=reductable_amount,
                                        status='Returned')
        order.total_price -= reductable_amount
        order.save()
    else:
        reductable_amount=item.product.offer*item.quantity
        thewallet, created = wallet.objects.get_or_create(user=request.user, defaults={'balance': Decimal('0')})
        thewallet.balance += reductable_amount
        thewallet.save()
        transactions.objects.create(user=request.user,order=order,payment_type='razorpay',amount=reductable_amount,
                                        status='Returned')
        size_variant = item.size_variant
        if size_variant:
                        # Increase the stock by the quantity in the order
            size_variant.stock += item.quantity
            item.quantity=0
            size_variant.save()
            item.status='returned'
            item.save()
        print('===========================price backed==================================')
        order.total_price-=reductable_amount
        order.save()



    return redirect('orderdetails',id=order.id)

def change_order_status(request,id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    alpha = get_object_or_404(AlOrder,id=id)
    if request.method=='POST':
        newstatus = request.POST.get('status')
        if alpha.status == 'pending' or alpha.status=='completed':
            alpha.status=newstatus
            alpha.save()
        messages.error(request,'only change the order if the order is pending')

    return redirect('admin_order_list')


def add_address_checkout(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
   
    
    kerala_districts = [
    "alappuzha", "ernakulam", "idukki", "kottayam", "kozhikode", 
    "malappuram", "palakkad", "pathanamthitta", "thiruvananthapuram", 
    "thrissur", "wayanad", "kannur", "kasaragod", "angamaly"
    ]

    states_in_india = [
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", 
    "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", 
    "karnataka", "kerala", "madhya pradesh", "maharashtra", "manipur", 
    "meghalaya", "mizoram", "nagaland", "odisha", "punjab", "rajasthan", 
    "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh", 
    "uttarakhand", "west bengal"
    ]

    user = request.user
    address = useraddress.objects.filter(user=user).all()

    if request.method == 'POST':
        print('========================================================================================================')
        error = ''
        address = useraddress.objects.filter(user=user).all()
        fullname = request.POST.get('fullname')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postalcode = request.POST.get('postalcode')
        landmark = request.POST.get('landmark')
        phonenumber = request.POST.get('phonenumber')
        print(fullname,city,state,postalcode,landmark,phonenumber)
        if fullname is None or city is None or state is None  or   postalcode is None or landmark is None or phonenumber is  None:
            error = 'every fields should be perfect '
        if  phonenumber is None or len(phonenumber)>10   :
            error = 'Phone should be ten digits'
        if  postalcode is None or len(postalcode)>6 :
            error = 'enter a valid postal code'
        if  state is None or state.lower() not  in states_in_india:
            error = 'enter a valid state'
        
        if  phonenumber is None or  phonenumber.isdigit()== False or postalcode.isdigit() == False:
            error = 'enter a valid pincode'
        if useraddress.objects.filter(user=user,fullname=fullname,
                                   city=city,state=state,
                                   postal_code = postalcode,
                                   landmark=landmark,phone_number=phonenumber):
            error='addres already exists'
        if error:
            messages.error(request,error)
            return  redirect('checkout')
        useraddress.objects.create(user=user,fullname=fullname,
                                   city=city,state=state,
                                   postal_code = postalcode,
                                   landmark=landmark,phone_number=phonenumber)
        
        
        
        return redirect('checkout')
    
    return redirect('checkout')

def review(request,id,id2):
    print('=======================================')
    try:
        alpha = get_object_or_404(Products,id=id)
    except  UnboundLocalError:
        messages.error(request,'Item is sold out')
        return redirect('orderdetails',id=order.id)
    except  Products.DoesNotExist:  
        messages.error(request,'Item is sold out')
        return redirect('orderdetails',id=order.id)

    order = get_object_or_404(AlOrder,id=id2)
    
        
   
    if request.method == 'POST':
        rating = request.POST.get('rating')
        review = request.POST.get('review')
        if not rating or not review:
            messages.error(request,'rating or review is empty')
            return redirect('orderdetails',id=order.id)
        if Review_ration.objects.filter(user=request.user,product=alpha).exists():
            messages.error(request,'U have already done review for this product')
            return redirect('orderdetails',id=order.id)

     
        try:
            Review_ration.objects.create(product=alpha,user=request.user,rating=rating,review=review)
        except Exception as e:
            messages.success(request,'review submitted sucessfully')


    return redirect('orderdetails',id=order.id)



def invoice_download(request,id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    print('=====================================') 
    alpha = get_object_or_404(AlOrder,id=id)

    context = {
        'order':alpha,
        'address':alpha.address
    }
    html_string = render_to_string('invoice_download.html',context)
    html = HTML(string=html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Invoice_{alpha.id}.pdf"'
    html.write_pdf(response)

    return response