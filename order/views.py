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
from django.urls import reverse
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required







@login_required(login_url='login_user')
def placeorder(request):
    
    if not request.user.is_authenticated:
        return redirect('login_user')
    if request.method == 'POST':
        address_id = request.POST.get('selected_address_id')
        payment_type = request.POST.get('payment_type')
        print(payment_type)
        print(address_id,'----------------------------------------------------------')
        cart_total =  cart_total_cal(request)
        


        if not address_id:
            messages.error(request, 'Please select an address.')
            return redirect('checkout')
        
        address = useraddress.objects.get(user=request.user,id=address_id)


        gama = Cart.objects.filter(user=request.user).first()
        if not gama:
            messages.error(request, 'Your cart is empty. Please add items before proceeding.')
            return redirect('checkout')

        items = Cartitems.objects.filter(cart=gama,product__is_active=True,product__catagory__is_active=True)
        coupon_obj = None
        # Calculate the cart total
        real_price = cart_total_cal(request)
        
        
        print('cart total:',cart_total)
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
        if applied_coupon:
            coupon_obj = coupons.objects.get(id=applied_coupon['id'])
            cart_total = Decimal(cart_total)
            discount =  cart_total * (Decimal(applied_coupon['discount_value']) / Decimal(100))
            cart_total -= discount
            print('cart after discount',cart_total)
            
        # Get the selected shipping address
        shipping_address = useraddress.objects.filter(id=address_id, user=request.user).first()
        if not shipping_address:
            messages.error(request, 'Invalid address selection.')
            return redirect('checkout')

        if cart_total == 0:
            messages.error(request, 'No products have been added')
            return redirect('checkout')
        if payment_type == 'cash_on_delivery':
            print('====================awef=======================asdf')
            sample = round(cart_total)
            print('rounded cart',sample)
            if sample > 1000:
                print('==================== Cart total is less than 1000 =====================')

                messages.error(request,'COD only availabe for purchase above 1000 rupees')
                return redirect('checkout')
        print('realprice',real_price)
        # Razorpay integration for online payment
        if payment_type == 'razorpay':
            order = AlOrder.objects.create(
                user=request.user,
                address=shipping_address,
                payment_method='Not completed', 
                total_price=cart_total+150,
                real_price=real_price,
                coupon = coupon_obj,
                status='Failed',
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            

            try:
                # Initialize Razorpay client
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

                # Create Razorpay order
                # In placeorder view
                cart_total = cart_total+150
                razorpay_order = client.order.create({
                'amount': int((cart_total ) * 100),  # Amount in paisa
                'currency': 'INR',
                'payment_capture': '1',
                 })

                # Save order details locally
                request.session['razorpay_order_id'] = razorpay_order['id']
                request.session['address_selected'] = address_id
                
                # print('2222222222222222222222222222222222222222')
                # success,error = _finalize_order(request, items, order)
                # print(cart_total)
                # if not success:
                #     messages.error(request,error)
                #     return redirect('checkout')
                return render(request, 'payment_page.html', {
                    'razorpay_order_id': razorpay_order['id'],
                    'razorpay_key': settings.RAZORPAY_KEY_ID,
                    'amount':round(cart_total) ,
                    'user_email': request.user.email,
                    'user_contact': address_id,  
                    'order':order,
                })
            except Exception as e:
                AlOrder.objects.filter(id=order.id).delete()
                messages.error(request, f"Error creating Razorpay order: {str(e)}")
                return redirect('checkout')
         
        elif payment_type == 'cash_on_delivery': 
            
            order = AlOrder.objects.create(
                user=request.user,
                address=shipping_address,
                payment_method=payment_type,
                total_price=cart_total+150,
                real_price=real_price,
                coupon = coupon_obj,
                status='pending',
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
           
            
            if order.coupon:
                try:
                    
                    if order.coupon.usage_limit>0:
                        order.coupon.usage_limit-=1
                        order.coupon.save()
                        del request.session['applied_coupon']
                    else:
                        AlOrder.objects.filter(id=order.id).delete()
                        raise ValueError("Coupon usage limit has been exceeded.")
                except:
                    raise ValueError("Coupon usage limit has  exceeded.")
                
                    
            success,error = _finalize_order(request, items, order)
            if not success:
                messages.error(request,error)
                return redirect('checkout')

            return render(request, 'success.html', {'order': order})

        else:
            messages.error(request, 'Invalid payment method.')
            return redirect("checkout")

    return redirect('checkout')

def _finalize_order(request, items, order):
    print("this is _finalize_order func")
    """Helper function to finalize the order: deduct stock and clear cart."""
    try:
        with transaction.atomic():
            for item in items:
                
                print('========================= product reached')
                product = item.product
                size_variant = product.size_variant.filter(size=item.size).first()
                if size_variant:
                    print('========================================pri')
                    if size_variant.stock < item.quantity:
                        print('================================')
                        error = f"Not enough stock for {product.name} - {size_variant.size}"
                        messages.error(request,f'{error}')
                        return False,error
                    size_variant.stock -= item.quantity
                    size_variant.save()
                    real_price = Decimal(order.real_price)
                    print('real price',real_price)
                    minus = item.product.offer*(Decimal(item.product.catagory.offer)/100)
                    item_price = item.product.offer-minus
                    price = item_price*item.quantity
                    print('price',price)
                    
                    if order.coupon:
                        price_ = item_price*item.quantity
                        aldiscount = price_*(Decimal(order.coupon.discount_value)/100)
                        price-=aldiscount
                        

                    


                AlOrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=price,
                    size_variant=size_variant,
                )
                print('========================================product added')
                
            # Clear cart
                Cart.objects.filter(user=request.user).delete()
                print('cart is deleted======================================================')
        return True, None 
    except Exception as error:
        print(error)
        return False,error


@login_required(login_url='login_user')
def razorpay_callback(request,id):
    print("this is razorpay_callback func")
    if not request.user.is_authenticated:
        return redirect('login_user')
    order = get_object_or_404(AlOrder,id=id)
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

            
            success,error = _finalize_order(request, items, order)
            if not success:
                messages.error(request,error)
                return redirect('checkout')
            order.razorpay_order_id=razorpay_order_id
            print('razorpay_order_id have been asigned')


            
            order.status = 'completed'
            order.payment_method = 'razorpay'
            print('order status changed to completed')
            order.save()
            print('deleted coupon')
            if order.coupon:
                try:
                    
                    if order.coupon.usage_limit>0:
                        order.coupon.usage_limit-=1
                        order.coupon.save()
                        del request.session['applied_coupon']
                    else:
                        AlOrder.objects.filter(id=order.id).delete()
                        raise ValueError("Coupon usage limit has been exceeded.")
                except:
                    raise ValueError("Coupon usage limit has  exceeded.")

            print('-----3333333333333333333333333333333333333333333333333333333333333333')
            return JsonResponse({"status": "success", "redirect_url": reverse('success', args=[order.id])})


        except Exception as e:
            print(f"Error in Razorpay verification: {e}")
            # Optionally delete the order
            AlOrder.objects.filter(id=order.id).delete()
            return JsonResponse({"status": "failure", "error": str(e)})

    return redirect('checkout')

@login_required(login_url='login_user')
def success(request,order_id):
    print("this is success page")
    if not request.user.is_authenticated:
        return redirect('login_user')
    order = AlOrder.objects.get(id=order_id)
    return render(request,'success.html',{'order':order})

@login_required(login_url='login_user')
def failure(request,id):
    print("this is failure page")
    try:
        order = get_object_or_404(AlOrder,id=id)
        AlOrder.objects.filter(id=order.id).delete()
    except Exception as e :
        print(f'failure_page = {e}')
    return render(request,'failure.html')


@login_required(login_url='login_user')
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
                if coupon.usage_limit==0:
                    messages.error(request,'The coupon limit expired')
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


@login_required(login_url='login_user')
def orderlist(request):
    details = AlOrder.objects.filter(user=request.user).all()
    context = {
        'orderdetails':details,
        'active_tab': 'orders'
    }

    return render(request,'userprofile.html',context)

@login_required(login_url='login_user')
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



@login_required(login_url='login_user')
def  cancel_order(request, id):
    # Fetch the order
    if not request.user.is_authenticated:
        return redirect('login_user')
    order = get_object_or_404(AlOrder, id=id, user=request.user)
    reason = request.POST.get('reason')
    if not reason.strip() or len(reason.strip()) < 10:
        messages.error(request, 'Please provide a valid reason ')
        return redirect('orderdetails', id)

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
                if order.status=='completed':
                    thewallet, created = wallet.objects.get_or_create(user=order.user.id, defaults={'balance': Decimal('0')})
                    thewallet.balance += order.real_price
                    thewallet.save()
                    transactions.objects.create(user=order.user,order=order,payment_type='razorpay',amount=order.real_price,
                                        status='Canceled')
                # Update the order status to 'canceled'
                order.status = 'canceled'
                order.reason=reason
                order.save()
               
 
            messages.success(request, 'Your order has been successfully canceled, and stock has been updated.')
        except Exception as e:
            print(e)
            messages.error(request, f'Error occurred while canceling the order: {str(e)}')
    else:
        messages.error(request, 'You cannot cancel this order as it is no longer pending.')

    # Redirect back to the order details page
    return redirect('orderdetails',id=id)

# ============================================admin=======================admin===================================================
@login_required(login_url='adminlogin')
def admin_order_list(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    the_mail = None
    search_query = request.GET.get('search', '').strip()
    alpha = AlOrder.objects.order_by('-id').all()
    for val in alpha:
        if not val.user.email:
            
            try:
                social = SocialAccount.objects.get(user=val.user,provider='google')
                the_mail = social.extra_data.get('email')
            except SocialAccount.DoesNotExist:
                the_mail = None
            if the_mail:
                val.user.email=the_mail
                val.save()
    
    if search_query:
        alpha = alpha.filter(
            Q(id__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    paginator = Paginator(alpha, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    
    context = {
        'items': page_obj,
        'search_query': search_query
    }
    return render(request,'admin/orders_list.html',context)

@login_required(login_url='adminlogin')
def admin_order_details(request,id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    try:
        alpha = get_object_or_404(AlOrder,id=id)
    except AlOrder.DoesNotExist:
        
        return render(request,'admin/order_edit.html',{'item':alpha})
    return render(request,'admin/order_edit.html',{'item':alpha})


@login_required(login_url='login_user')
def indiviudalcancel(request,id,id2):
    if not request.user.is_authenticated:
        return redirect('login_user')
    print('===========================================')
    order = get_object_or_404(AlOrder,id=id)
    item = get_object_or_404(AlOrderItem,id=id2)
    items = AlOrderItem.objects.filter(order=order).all()
    reason = request.GET.get('reason', '').strip()

        # Validate the reason
    if not reason or len(reason) < 10:
        messages.error(request, 'Please provide a valid reason ')
        return redirect('orderdetails', id)
        
   
    if order.status == 'completed' :
        cart = order.real_price
        if order.coupon:

            reductable_amount = item.price
            print('reductable amount',reductable_amount)

            size_variant = item.size_variant
            if size_variant:
                        # Increase the stock by the quantity in the order

                size_variant.stock += item.quantity
                size_variant.save()
                item.reason = reason
                item.save()
            
            thewallet, created = wallet.objects.get_or_create(user=request.user, defaults={'balance': Decimal('0')})
            thewallet.balance += reductable_amount
            thewallet.save()
            transactions.objects.create(user=request.user,order=order,payment_type='razorpay',amount=reductable_amount,
                                        status='Canceled')
            if (items.filter(status='cancelled').count())+1==items.count():
                order.status='canceled'
            print((items.filter(status='cancelled').count()))
            print(items.count())
            order.total_price -= reductable_amount
            order.save()
        else:
            reductable_amount = item.price
            print('reductable amount',reductable_amount)

            thewallet, created = wallet.objects.get_or_create(user=request.user, defaults={'balance': Decimal('0')})
            thewallet.balance += reductable_amount
            thewallet.save()
            transactions.objects.create(user=request.user,order=order,payment_type='razorpay',amount=reductable_amount,
                                        status='Canceled')
            if (items.filter(status='cancelled').count())+1==items.count():
                order.status='canceled'
            print((items.filter(status='cancelled').count()))
            print(items.count())
            size_variant = item.size_variant
            if size_variant:
                        # Increase the stock by the quantity in the order
                size_variant.stock += item.quantity
                size_variant.save()
                item.save()
            print('=============================================================')
            order.total_price-=reductable_amount
            print('order total',order.total_price)
            
        
    if order.status == 'pending' or order.status == 'canceled':
        cart = order.real_price
        if order.coupon:
            print(cart)
            reductable_amount = item.price
            print('reductable amount',reductable_amount)
            
            
            size_variant = item.size_variant
            if (items.filter(status='cancelled').count())+1==items.count():
                order.status='canceled'
                print((items.filter(status='cancelled').count()))
                print(items.count())
            if size_variant:
                        # Increase the stock by the quantity in the o   rder
                size_variant.stock += item.quantity
                size_variant.save()
                item.save()
            
            order.total_price-=reductable_amount
            print(order.total_price)


        else:
            if (items.filter(status='cancelled').count())+1==items.count():
                order.status='canceled'
            print((items.filter(status='cancelled').count()))
            print(items.count())
            size_variant = item.size_variant
            if size_variant:
                        # Increase the stock by the quantity in the order
                size_variant.stock += item.quantity
                size_variant.save()
                item.save()
             

   
    if order.total_price<150:
        order.total_price=0
    
    order.save()
    item.status='cancelled'
    item.save()
    messages.success(request,'Item canceled succesfully')
    return redirect('orderdetails',id=order.id)


@login_required(login_url='login_user')
def individual_return(request,id,id2):
    if not request.user.is_authenticated:
        return redirect('login_user')
    print('===========================================')
    order = get_object_or_404(AlOrder,id=id)
    item = get_object_or_404(AlOrderItem,id=id2)
    items = AlOrderItem.objects.filter(order=order).all()
    reason = request.POST.get('reason')
    cart = cart_total_cal(request)
    cart = order.real_price
    print('etheeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
    if item.status=='pending':
        item.status='requested'
        print('etheeeeeeeeeeeeeeeee3222222222222222222222222eeeeeeeeeeeeeeeeeeeeeeee')
        item.save()
        return redirect('orderdetails',id=order.id)

    if order.coupon:
        reductable_amount = item.price
        print('reductable amount',reductable_amount)

        
            
        size_variant = item.size_variant
        if (items.filter(status='returned').count())+1==items.count():
            order.status='returned'
            print((items.filter(status='returned').count()))
            print(items.count())
        if size_variant:
                        # Increase the stock by the quantity in the order
            size_variant.stock += item.quantity
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

        reductable_amount = item.price
        print('reductable amount',reductable_amount)

        thewallet, created = wallet.objects.get_or_create(user=request.user, defaults={'balance': Decimal('0')})
        thewallet.balance += reductable_amount
        thewallet.save()
        transactions.objects.create(user=request.user,order=order,payment_type='razorpay',amount=reductable_amount,
                                        status='Returned')
        size_variant = item.size_variant
        if (items.filter(status='returned').count())+1==items.count():
            order.status='returned'
            print((items.filter(status='returned').count()))
            print(items.count())
        if size_variant:
                        # Increase the stock by the quantity in the order
            size_variant.stock += item.quantity
            size_variant.save()
            item.status='returned'
            item.save()
        print('===========================price backed==================================')
        
        order.total_price-=reductable_amount
        order.save()



    return redirect('admin_order_details',id=order.id)

@login_required(login_url='adminlogin')
def change_order_status(request,id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    alpha = get_object_or_404(AlOrder,id=id)
    if request.method=='POST':
        newstatus = request.POST.get('status')
        if alpha.status == 'pending' or alpha.status=='completed':
            alpha.status=newstatus
            alpha.save()

    return redirect('admin_order_list')


@login_required(login_url='login_user')
def add_address_checkout(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
   
    data = request.session.get('form-data',{})
    if data:
        del request.session['form-data']
        
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
        if not fullname or not city or not state or not postalcode or not landmark or not phonenumber:
            error = 'every fields should be perfect '
        if fullname.strip()=='':
            error = 'Enter a Valid Name'
        if len(fullname)<5:
            error = 'full name should be at least 5 letter'
        if any(char.isdigit() for char in fullname):
            error = 'Name cannot include numbers'
        
        if landmark.strip()=='':
            error = 'Enter a Valid landmark'
        
        
        if landmark.strip()=='':
            error = 'Enter a Valid landmark'
        
        if city.strip()=='':
            error = 'city should be valid'
        if city.isdigit()==True:
            error = 'city should not be a number' 
        
        if   len(phonenumber)>10 or len(phonenumber)<10:
            error = 'Phone should be ten digits'
        if any(char.isalpha() for char in phonenumber ):
            error = 'phone number can only contain numbers'
        if   phonenumber.isdigit()==False:
            error = 'Enter a valid phonenumber'
        
        



        if  len(postalcode)>6:
            error = 'enter a valid postal code'
        if   postalcode.isdigit() == False:
            error = 'enter a valid pincode'

        
        if  state.lower() not  in states_in_india:
            error = 'enter a valid state'
        
        
        
        if useraddress.objects.filter(user=user,fullname=fullname,
                                   city=city,state=state,
                                   postal_code = postalcode,
                                   landmark=landmark,phone_number=phonenumber).exists():
            error='addres already exists'
        if error:
            request.session['form-data']= {
                'dropdown_open':True,
                'fullname':fullname,
                'city':city,
                'state':state,
                'postal_code':postalcode,
                'landmark':landmark,
                'phonenumber':phonenumber,
                'error':error
            }
            return redirect('checkout')
        useraddress.objects.create(user=user,fullname=fullname,
                                   city=city,state=state,
                                   postal_code = postalcode,
                                   landmark=landmark,phone_number=phonenumber)
        
        
        
        return redirect('checkout')
    
    return redirect('checkout')


def admin_review(request):
    return render(request,'admin/page-reviews.html')


@login_required(login_url='login_user')
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


@login_required(login_url='login_user')
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

@login_required(login_url='login_user')
def retry_razorpay_payment(request,id):
    print('this is razorpay retry')
    order = get_object_or_404(AlOrder,id=id)
    cart_total = order.total_price
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create Razorpay order
        razorpay_order = client.order.create({
            "amount": int(cart_total * 100),  # Amount in paise
            "currency": "INR",
            "receipt": str(order.id)
        })
        order.razorpay_order_id = razorpay_order['id']
        order.save()
             
        
        return render(request, 'payment_page.html', {
                    'razorpay_order_id': order.razorpay_order_id,
                    'razorpay_key': settings.RAZORPAY_KEY_ID,
                    'amount':cart_total ,
                    'user_email': request.user.email,
                    'user_contact': order.address,  
                    'order':order,
                })
    except Exception as e:
        AlOrder.objects.filter(id=order.id).delete()
        messages.error(request, f"Error creating Razorpay order: {str(e)}")
        return redirect('orderdetails' ,id=order.id)
    

@login_required(login_url='login_user')
def  return_order(request, id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    order = get_object_or_404(AlOrder, id=id)
    print('etheeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
    reason = request.POST.get('reason')
    if not order.request:
        order.request = 'requested'
        order.save()
        return redirect('orderdetails',id=id)
    
    
    if order.status == 'delivered':
        print('==============////////////////////////==========================================================')
        try:
            with transaction.atomic():

                for item in order.items.all():
                    item.status = 'Returned'
                    item.save()
                    size_variant = item.size_variant
                    if size_variant:
                        
                        size_variant.stock += item.quantity
                        size_variant.save()
                
                thewallet, created = wallet.objects.get_or_create(user=order.user.id, defaults={'balance': Decimal('0')})
                thewallet.balance += order.real_price
                thewallet.save()
                transactions.objects.create(user=order.user,order=order,payment_type='razorpay',amount=order.real_price,
                                        status='Returned')
                
                order.status = 'returned'
                order.request = None
                order.save()
              
               
 
            messages.success(request, 'Your order has been successfully canceled, and stock has been updated.')
        except Exception as e:
            print(f'Error occurred while canceling the order: {str(e)}')
    else:
        messages.error(request, 'You cannot cancel this order as it is no longer pending.')

    
    return redirect('admin_order_details',id=order.id)

# ==========