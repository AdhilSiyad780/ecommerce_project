from django.shortcuts import render,redirect
from .models import catagory
from django.shortcuts import get_object_or_404
# Create your views here.





def catagory_list(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')

    item = catagory.objects.all()

    return render(request,'admin/catagory_list.html',{'item':item})

def create_catagory(request):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    item = catagory.objects.all()
    error = ''
    try:
        if request.method == "POST":
            name = request.POST.get('name')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            offer = request.POST.get('offer')
            if offer>60:
                error='offer should be less than 60%'
                return render(request,'admin/catagory_list.html',{{'item':item,'createerror':error}})

            alpha = catagory.objects.create(name=name,description = description,image = image,offer=offer)
            alpha.save()
            return redirect('catagory_list')
    except Exception  as e:
        error = 'An error occured while creating'
        return render(request,'admin/catagory_list.html',{{'item':item,'createerror':error}})
    
    
    return render(request,'admin/catagory_list.html',{'item':item})
    

def edit_catagory(request,id):
    if request.user.is_staff==False or not request.user.is_authenticated:
        return redirect('adminlogin')
    alpha = get_object_or_404(catagory,id=id)
    item = catagory.objects.all()
    try:
        if request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('deurscription')
            image = request.FILES.get('image')
            offer = request.POST.get('offer')
            alpha.name = name
            if description:
                alpha.description=description
            if image:
                alpha.image = image
            if offer>60:
                error='offer should be less than 60%'
                return render(request,'admin/catagory_list.html',{{'item':item,'createerror':error}})
            if offer:
                alpha.offer = offer
            print('=====================================')
            alpha.save()

            return redirect('catagory_list')
    except Exception as e:
        print('the error that occured is -- {e}')
        
    
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

