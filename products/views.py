from django.shortcuts import render,redirect
from .models import Products,SizeVariant,Review_ration
from Catagory.models import catagory
import imghdr
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from products.models import Products
from decimal import Decimal,InvalidOperation
from django.db.models import Avg
from django.db.models import Case, When
from PIL import Image
from django.contrib.auth.decorators import login_required




# Create your views here.
from PIL import Image

def is_valid_image(filename):
    try:
        im = Image.open(filename)
        im.verify()
        im.close()
        im = Image.open(filename) 
        im.transpose(Image.FLIP_LEFT_RIGHT)
        im.close()
        return True
    except: 
        print(filename,'corrupted')
        return False


@login_required(login_url='adminlogin')
def product_list(request):
    # Restrict access to staff or authenticated users
    if not request.user.is_staff or not request.user.is_authenticated:
        return redirect('adminlogin')
    
    # Fetch the search term from GET parameters
    search_query = request.GET.get('search', '').strip()
    products = Products.objects.order_by('-id').all()

    # Filter products based on the search query
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Debug the queryset
    print(products)  # Debugging line

    # Paginate the product list (5 products per page)
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render the template with the paginated products
    return render(request, 'admin/product_list.html', {
        'item': page_obj,
        'search_query': search_query
    })


@login_required(login_url='adminlogin')
def edit_product(request, id):
    if not request.user.is_staff or not request.user.is_authenticated:
        return redirect('adminlogin')

    alpha = get_object_or_404(Products, id=id)
    cata = catagory.objects.filter(is_active=True)
    error = ''

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        offer = request.POST.get('offer')
        price = request.POST.get('price')
        image1=request.FILES.get('image1')
        image2=request.FILES.get('image2')
        image3=request.FILES.get('image3')



        # Update fields with validation
        if name.strip()=='':
            error='Enter a valid name'
        if len(name.strip())<5:
            error='description should be greater than 5 charactors'
        if description.strip()=='':
                error='Enter a valid name'
        if len(description.strip())<10:
            error='description should be greater than 10 charactors'
        # if not price.isdigit():
        #         error='pirce should be a number'
        # if not offer.isdigit():
        #     error='offer should be a number'
        
        
        try:

    # Convert price and offer to Decimal
            price = Decimal(price)
            offer = Decimal(offer)

    # Check if price and offer are greater than zero
            if price <= 0:
                error = 'The price should be a valid number greater than zero.'
    
            if offer <= 0:
                error = 'The offer should be a valid number greater than zero.'
           
    # Check if price is greater than or equal to offer
            if price < offer:
               error = 'The price should be greater than offer.'

        except InvalidOperation:
    # If the price or offer cannot be converted to a valid Decimal
            error = 'The price and offer should be valid numbers.'

        if image1:
            if not  is_valid_image(image1):
                error='the image is not valid'
        if image2:
            if not  is_valid_image(image2):
                error='the image is not valid'
        if image3:
            if not  is_valid_image(image3):
                error='the image is not valid'
        if error:
            print(error)
            return render(request,'admin/edit_product.html', {'cata': cata, 'item': alpha, 'error': error})
            


        # Save if no errors
        if not error:
            alpha.name=name
            alpha.description=description
            alpha.offer=offer
            alpha.price=price
            if image1:
                alpha.image1=image1
                print('image one is saved')
            if image2:
                alpha.image2=image2
            if image3:
                alpha.image3=image3
            alpha.save()
            return redirect('product_list')

    return render(request, 'admin/edit_product.html', {'cata': cata, 'item': alpha, 'error': error})

@login_required(login_url='adminlogin')
def create_product(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    alpha = catagory.objects.filter(is_active = True)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        offer = request.POST.get('offer')
        price = request.POST.get('price')
        catagory_id = request.POST.get('catagory_id')
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2') 
        image3 = request.FILES.get('image3')
        error = ''
        print(name,description,offer,price,catagory_id,image1,image2,image3)
        
        try:
            if not name or not description or not offer or not price or not catagory_id or not image1 or not image2 or not  image2 or not image3:
                error='All field is compalsary'  
            if name.strip()=='':
                error='Enter a valid name'
            if len(name.strip())<5:
                error='description should be greater than 5 charactors'
            if description.strip()=='':
                error='Enter a valid name'
            if len(description.strip())<10:
                error='description should be greater than 10 charactors'
            if not price.isdigit():
                error='pirce should be a number'
            if not offer.isdigit():
                error='offer should be a number'

                
            if float(price)<=0:
                error='the price should be a valid number'
            if float(offer)<=0:
                error='the offer should be a valid numbeer'
            if float(price)<float(offer) or float(offer)>float(price) :
                error='the price should be greater than the offer '
            if  is_valid_image(image2) is False:
                error='invalid format of image'
            if  is_valid_image(image2) is False:
                error='invalid format of image'
            if  is_valid_image(image2) is False:
                error='invalid format of image'
            
            
            if error:    
                print(error)
                context = {
                    'name':name,
                    'description':description,
                    'offer':offer,
                    'price':price,
                    'item':alpha,'error':error
                    
                }
                return render(request,'admin/create_product.html',context)     
            Catagory = catagory.objects.get(id=catagory_id)
            product = Products.objects.create(catagory=Catagory,name=name,description=description,price=price,offer=offer,image1=image1,image2=image2,image3=image3)
            product.save()
            print('product created')
            return redirect('product_list')
        except catagory.DoesNotExist:
            return render(request,'admin/create_product.html',{'item':alpha})

               
        except Exception as e:
            error = f'The error is {e}'
            return render(request,'admin/create_product.html',{'item':alpha})
        

    return render(request,'admin/create_product.html',{'item':alpha})

@login_required(login_url='adminlogin')
def unlist_product(request,id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    alpha = get_object_or_404(Products,id = id)
    try:
        if alpha.is_active:
            Products.objects.filter(id=alpha.id).update(is_active = False)
        else:
            Products.objects.filter(id=alpha.id).update(is_active = True)
    except Exception as e:
        item = Products.objects.all()
        print(f'the problem is------- {e}')
        error = f' an exception occured--------------{e}'
        return render(request,'admin/product_list.html',{'error':error,'item':item})

    return redirect('product_list') 

#==================================================================================================================================
@login_required(login_url='adminlogin')
def list_variant(request,product_id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    passid = product_id
    # try:
    alpha = get_object_or_404(Products,id=product_id)

    variants = SizeVariant.objects.filter(product=alpha.id).order_by('id')
     
    paginator = Paginator(variants,3)
    pagenumber = request.GET.get('page')
    page_obj = paginator.get_page(pagenumber)

    return render(request,'admin/list_variant.html',{'variants':variants,'product_id':passid,'item':page_obj })

@login_required(login_url='adminlogin')
def create_variant(request,product_id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    print('=================================')
    product_id = get_object_or_404(Products,id = product_id)
    
    if request.method == 'POST':
        size = request.POST.get('size')
        stock = request.POST.get('stock')
        print(product_id,size,stock)
        error = ''
        try:
            print('====================================================')
          
            if stock is None:
                error = 'stock cant be empty'
            if int(stock) < 0:
                error = 'stock must be greater than zero'
             
                
            if SizeVariant.objects.filter(product = product_id,size=size).exists():
                error = 'This size already exists'
            if error:
                return render(request,'admin/create_variant.html',{'error':error,'product_id':product_id })

            
            alpha = SizeVariant.objects.create(product = product_id,size=size,stock=stock)
            alpha.save()
            return redirect('list_variant',product_id=product_id.id)
        
            
        except ValueError:
            error = "no field cannot be empty"

            
    return render(request,'admin/create_variant.html',{'product_id':product_id})
        
@login_required(login_url='adminlogin') 
def edit_variant(request,variant):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    alpha = get_object_or_404(SizeVariant,id=variant)
    error=''
    if request.method == 'POST':
        stock = request.POST.get('stock')
        size = request.POST.get('size')
        if not stock.isdigit() or int(stock) < 0:
            error = 'Stock must be a positive number.'
        
        if error:
            return render(request,'admin/edit_variant.html',{'error':error,'alpha':alpha})
        
        alpha.stock=int(stock)
        alpha.size = size
        alpha.save()
        return redirect('list_variant',product_id = alpha.product.id)


    return render(request,'admin/edit_variant.html',{'alpha':alpha})



# =============================================================USER======================================================================
    
@login_required(login_url='login_user')
def display_products(request):
    alpha = Products.objects.filter(is_active=True,catagory__is_active=True)
    cata = catagory.objects.filter(is_active = True)

    sort = request.GET.get('sort','')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    alcata = request.GET.get('category')
    rating = request.GET.get('rating')
    search_term = request.GET.get('search','')
    if search_term:
        alpha = alpha.filter(name__icontains=search_term)

   
    if sort == 'low_to_high':
        alpha = alpha.order_by('price')
    if sort == 'high_to_low':
        alpha = alpha.order_by('-price')
    if min_price and max_price:
        alpha=alpha.filter(price__gte=min_price,price__lte=max_price)
    if min_price:
        alpha = alpha.filter(price__gte=min_price)
    if max_price:
        alpha = alpha.filter(price__lte=max_price)
    if alcata:
        alpha = alpha.filter(catagory__id=alcata)
    if sort == 'name_asc':
        alpha = alpha.order_by('name')
    if sort == 'name_desc':
        alpha = alpha.order_by('-name')
    print(search_term,'=====================================================================')
    
    
    page = request.GET.get('page', 1) 
    paginator = Paginator(alpha, 6)  
    try:
        products = paginator.page(page) 
    except PageNotAnInteger:
        products = paginator.page(1) 
    except EmptyPage:
        products = paginator.page(paginator.num_pages)  

    return render(request, 'shop.html', {'item': products,
                                          'cata': cata,
                                          'search_term':search_term,
                                          'sort':sort,
                                          
                                          })



@login_required(login_url='login_user')
def product_details(request,id):
    alpha = get_object_or_404(Products,id=id)
    reviews = Review_ration.objects.filter(product=alpha.id).all()
    
    sizes_order = ["S", "M", "L", "XL", "XXL"]
    size = alpha.size_variant.all().annotate(
        sort_order=Case(
            *[When(size=size, then=pos) for pos, size in enumerate(sizes_order)],
            default=len(sizes_order)
        )
    ).order_by("sort_order")

    rating = Review_ration.objects.filter(product=alpha).aggregate(average=Avg('rating'))
    print(rating)
    avg_rating = rating['average']
    if avg_rating:
        avg_rating=round(avg_rating)
    print('=======================')
    print(avg_rating)
    related = Products.objects.filter(name=alpha.name,catagory__is_active=True,is_active=True)[:3]
    context = {'alpha':alpha,'size':size,'related':related,'review':reviews,'rating':avg_rating}

    return render(request,'product_details.html',context)
    
