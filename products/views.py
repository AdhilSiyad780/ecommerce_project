from django.shortcuts import render,redirect
from .models import Products,SizeVariant,Review_ration
from Catagory.models import catagory
import imghdr
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
def is_valid_image(image_file):
    """
    Check if the uploaded file is an image.
    """
    # You can use imghdr to verify that the file is an image.
    if image_file:
        image_type = imghdr.what(image_file)
        return image_type in ['jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff']
    return False



def product_list(request):
    # Restrict access to staff or authenticated users
    if not request.user.is_staff or not request.user.is_authenticated:
        return redirect('adminlogin')
    
    # Fetch the search term from GET parameters
    search_query = request.GET.get('search', '').strip()
    products = Products.objects.all()

    # Filter products based on the search query
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Debug the queryset
    print(products)  # Debugging line

    # Paginate the product list (5 products per page)
    paginator = Paginator(products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render the template with the paginated products
    return render(request, 'admin/product_list.html', {
        'item': page_obj,
        'search_query': search_query
    })


    
    

def  edit_product(request,id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    alpha = get_object_or_404(Products,id=id)
    cata = catagory.objects.filter(is_active = True)
    
    if request.method == 'POST':
        
        name = request.POST.get('name')
        description = request.POST.get('description')
        offer = request.POST.get('offer')
        price = request.POST.get('price')
        catagory_id = request.POST.get('catagory_id')
        error = ''
        if name:
            alpha.name = name
        if description:
            alpha.description = description
        if offer:
            alpha.offer = offer
        if price:
            alpha.price = price
        
        if catagory_id:
            Catagory = catagory.objects.get(id = catagory_id)
            alpha.catagory = Catagory
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2') 
        image3 = request.FILES.get('image3')
        if image1:
            if is_valid_image(image1):
                alpha.image1 = image1
            else:
                error = 'image 1 is invalid'
        if image2:
            if is_valid_image(image2):
                alpha.image2 = image2
            else:
                error = 'image 2 is invalid'
        if image3:
            if is_valid_image(image3):
                alpha.image3 = image3
            else:
                error = 'image 3 is invalid'
        alpha.save()
        return redirect('product_list')
    return render(request,'admin/edit_product.html',{'cata':cata,'item':alpha})

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
            if int(price)<=0  or price is None :
                error = 'enter a valid price'
            if name is None:
                error = 'enter a valid name'
            if description is None:
                error = 'enter a valid description'
            if catagory_id is None:
                error = 'catagory should be included'
            if image1 is None or image2 is None or image3 is None:
                error = "Three images should be included"
            if int(offer)<=0 or int(offer)>int(price) or offer is None:
                error='enter a valid offer'
            
            if not  is_valid_image(image1):
                error = 'First image is not in image format'
            if not  is_valid_image(image2):
                error = 'Second image is not in image format'
            if not  is_valid_image(image3):
                error = 'Third image is not in image format'

            if error:
                return render(request,'admin/create_product.html',{'error':error,'item':alpha})
            Catagory = catagory.objects.get(id=catagory_id)
            product = Products.objects.create(catagory=Catagory,name=name,description=description,price=price,offer=offer,image1=image1,image2=image2,image3=image3)
            product.save()
            return redirect('product_list')
        except catagory.DoesNotExist:
            return render(request,'admin/create_product.html',{'item':alpha})

               
        except Exception as e:
            error = f'The error is {e}'
            return render(request,'admin/create_product.html',{'item':alpha})
        

    return render(request,'admin/create_product.html',{'item':alpha})

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
def list_variant(request,product_id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    passid = product_id
    # try:
    alpha = get_object_or_404(Products,id=product_id)

    variant = SizeVariant.objects.filter(product=alpha.id)

  

    return render(request,'admin/list_variant.html',{'item':variant,'product_id':passid},)

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
    

def display_products(request):
    alpha = Products.objects.filter(is_active=True)
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
    
    page = request.GET.get('page', 1)  # Get the page number from the URL
    paginator = Paginator(alpha, 6)  # 12 products per page
    try:
        products = paginator.page(page)  # Get products for the current page
    except PageNotAnInteger:
        products = paginator.page(1)  # If page is not an integer, deliver first page
    except EmptyPage:
        products = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page

    return render(request, 'shop.html', {'item': products, 'cata': cata})

from django.db.models import Case, When

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
    related = Products.objects.filter(name=alpha.name)[:3]
    context = {'alpha':alpha,'size':size,'related':related,'review':reviews}

    return render(request,'product_details.html',context)
    
