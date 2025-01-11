from django.shortcuts import render,redirect
from .models import catagory
from django.shortcuts import get_object_or_404
from products.views import is_valid_image
# Create your views here.





def catagory_list(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')

    item = catagory.objects.order_by('id').all()

    return render(request,'admin/catagory_list.html',{'item':item})

def create_catagory(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    item = catagory.objects.all()
    error=None
    try:
        if request.method == "POST":
            name = request.POST.get('name')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            offer = request.POST.get('offer')
            if not name or not description or not offer or not image:
                error='all fields are mantotory'
            if len(name)<8:
                error='name should be greater than 5 charactors'
            if name.strip()=='':
                error = 'Enter a valid name'
            if name.isdigit():
                error='Enter a valid  Name'
            if catagory.objects.filter(name=name).exists():
                error = 'catagory with this name already exists'
                return render(request,'admin/catagory_list.html',{'item':item,'createerror':error})

            if description.isdigit():
                error='Enter a valid  discription'
            if description.strip()=='':
                error = 'Enter a valid description'
            if catagory.objects.filter(description=description).exists():
                error = 'catagory with this description already exists'
                return render(request,'admin/catagory_list.html',{'item':item,'createerror':error})
            
            if not  is_valid_image(image):
                error = 'incorrect image format'
                return render(request,'admin/catagory_list.html',{'item':item,'createerror':error})
            




            if float(offer)>60:
                error='offer should be less than 60%'
            if float(offer)<0:
                error='offer cannot be less than zero'
            if error:
                return render(request,'admin/catagory_list.html',{'item':item,'createerror':error})

            alpha = catagory.objects.create(name=name,description = description,image = image,offer=offer)
            alpha.save()
            return redirect('catagory_list')
    except Exception  as e:
        error = f'An error occured while creating {e}'
        return render(request,'admin/catagory_list.html',{'item':item,'createerror':error})
    
    
    return render(request,'admin/catagory_list.html',{'item':item})
    

def edit_catagory(request,id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    alpha = get_object_or_404(catagory,id=id)
    item = catagory.objects.all()
    error =None
    try:
        if request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            offer = request.POST.get('offer')

            print(name,description,offer)
            if not name or not description or not offer:
                error='all fields are mantotory'
            elif len(name)<8:
                error='name should be greater than 5 charactors'
            elif name.strip()=='':
                error = 'Enter a valid name'
            elif name.isdigit():
                error='Enter a valid  Name'
           
            
            elif description.isdigit():
                error='Enter a valid  discription'
            elif description.strip()=='':
                error = 'Enter a valid description'
            elif float(offer)>60:
                error='offer should be less than 60%'
            elif float(offer)<0:
                error = 'offer cannot be less than zero'
                print(error)
            elif image:
                if not  is_valid_image(image):
                    error = 'incorrect image format'
                    return render(request,'admin/edit_catagory.html',{'item':item,'createerror':error})
            if error:
                print(error)
                return render(request,'admin/edit_catagory.html',{'item':alpha,'createerror':error})
            
            
            
            
            # if error:
            #     return render(request,'admin/edit_catagory.html',{'item':alpha,'createerror':error})

            
            alpha.name = name
            alpha.description=description
            if image:
                alpha.image = image
            
            alpha.offer = offer
            print('=====================================')
            alpha.save()

            return redirect('catagory_list')
    except Exception as e:
        error = (f'the error that occured is -- {e}')
        return render(request,'admin/edit_catagory.html',{'item':alpha,'createerror':error})
        
    
    return render(request,'admin/edit_catagory.html',{'item':alpha})
    
  
def unlist_catagory(request,id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    try:
        alpha = get_object_or_404(catagory,pk=id)
        if alpha.is_active:
            catagory.objects.filter(id=alpha.id).update(is_active = False)
        else:
            catagory.objects.filter(id=alpha.id).update(is_active = True)
    except Exception as e:
        item = catagory.objects.all()
        error = 'An unexpected Error occured during the event'
        return render(request,{'error':error,'item':item})

    return redirect('catagory_list')



#====================================================================================================================================================================

