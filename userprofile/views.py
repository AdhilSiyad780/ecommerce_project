from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password,make_password
from auth_user.views import send_otp_mail,otp_generetor
from auth_user.models import OTP
from django.contrib.auth import login

from django.utils import timezone
from datetime import timedelta
from .models import useraddress
from django.shortcuts import   get_object_or_404
from order.models import AlOrder
from django.contrib import messages
from Coupons.models import wallet,coupons
from transaction.models import transactions
from auth_user.models import Refferal




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
# Create your views here.

def userprofile(request):
    if  not  request.user.is_authenticated:
        return redirect('login_user')
    print('============================================================')
    user = request.user
    details = AlOrder.objects.filter(user=request.user).order_by('-id')
    

    address = useraddress.objects.filter(user=user).all()
    thewallet = wallet.objects.filter(user=request.user).first()
    trans = transactions.objects.filter(user=request.user).order_by('-created_at')[:5]
    referal_id = Refferal.objects.filter(user=request.user).first()
    print(thewallet)
    
    return render(request,'userprofile.html',{'user':user,'address':address,'active_tab': 'dashboard','orderdetails':details,'wallet':thewallet,'trans':trans,'ref':referal_id})

def updateprofile(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    print('===========================================================================================================================')
    user = request.user
    error = None 

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        

        if User.objects.filter(username=username).exclude(id=user.id).exists():
            error = 'Username already exists'
        if User.objects.filter(username=user).exists():
            error='please change the username'

        # Check if the email already exists
        elif User.objects.filter(email=email).exclude(id=user.id).exists():
            error = 'The email already exists'

        # Validate the password
        elif not check_password(password, user.password):
            error = 'Password does not match'

        if error:
            return render(request, 'userprofile.html', {
                'error': error,
                'active_tab': 'update-profile',  # Pass the tab information
            })
        otp = otp_generetor()
        expiry_time = timezone.now()+ timedelta(seconds=60)
 
        OTP.objects.update_or_create(email=email,defaults={'otp': otp, 'expires_at': expiry_time})

        request.session['registration'] = {'username':username,'email':email,'password':password }

        if not send_otp_mail(otp,email):
            error='Sending OTP  to your email failed'
            return render(request,'otp2.html',{'error':error})
        return redirect('verify_otp',email=email) 
        

    # If GET request, render the profile page
    return render(request, 'userprofile.html',{'active_tab': 'update-profile'})

def add_address(request):
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
        if not fullname or not city or not state or not postalcode or not landmark or not phonenumber:
            error = 'every fields should be perfect '
        if fullname.strip()=='':
            error = 'Enter a Valid Name'
        if len(fullname)<5:
            error = 'full name should be at least 5 letter'
        if any(char.isdigit() for char in fullname):
            error = 'Name cannot include numbers'
        if error:
            messages.error(request,error)
            return render(request,'userprofile.html',{'active_tab': 'address','address':address })
        
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
        if error:
            messages.error(request,error)
            return render(request,'userprofile.html',{'active_tab': 'address','address':address })
        



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
            messages.error(request,error)
            return render(request,'userprofile.html',{'active_tab': 'address','address':address })
        useraddress.objects.create(user=user,fullname=fullname,
                                   city=city,state=state,
                                   postal_code = postalcode,
                                   landmark=landmark,phone_number=phonenumber)
        
        
        
        return redirect('userprofile')
    
    return render(request,'userprofile.html',{'active_tab': 'address','address':address})


def editaddress(request, id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    user = request.user
    alpha = useraddress.objects.filter(user=user)
    # Fetch the specific address to be edited
    address = get_object_or_404(useraddress, id=id, user=user) 

    if request.method == 'POST':
        error = ''
        fullname = request.POST.get('fullname')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postalcode = request.POST.get('postalcode')
        landmark = request.POST.get('landmark')
        phonenumber = request.POST.get('phonenumber')

        # Validation checks
        if not fullname or not city or not state or not postalcode or not landmark or not phonenumber:
            error = 'every fields should be perfect '
        if fullname.strip()=='':
            error = 'Enter a Valid Name'
        if len(fullname)<5:
            error = 'full name should be at least 5 letter'
        if any(char.isdigit() for char in fullname):
            error = 'Name cannot include numbers'
        if error:
            messages.error(request,error)
            return redirect('userprofile')        

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
        if error:
            messages.error(request,error)
            return redirect('userprofile')        
        if  len(postalcode)>6:
            error = 'enter a valid postal code'
        if   postalcode.isdigit() == False:
            error = 'enter a valid pincode'

        
        if  state.lower() not  in states_in_india:
            error = 'enter a valid state'
        
        


        # Check if the address already exists (exclude the current address being edited)
        elif useraddress.objects.filter(user=user, fullname=fullname, city=city, state=state,
                                        postal_code=postalcode, landmark=landmark, phone_number=phonenumber).exclude(id=id):
            error = 'This address already exists.'

        if error:
            messages.error(request,error)
            return redirect('userprofile')
        # If no errors, update the address
        print('===================================================')
        address.fullname = fullname
        address.city = city
        address.state = state            

        address.postal_code = postalcode
        address.landmark = landmark
        address.phone_number = phonenumber
        address.save()  # Save the updated address instance
        messages.success(request,'updated address')
        # Redirect to the user profile or address list after success
        return redirect('userprofile')  # Assuming the URL name for the profile page is 'userprofile'

    # If GET request, render the address edit form with current details
    return render(request, 'userprofile.html', {'active_tab': 'address', 'address': alpha})



def delete_address(request,id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    alpha = get_object_or_404(useraddress,id=id)
    useraddress.objects.filter(id=alpha.id,user=request.user).delete()
    address = useraddress.objects.filter(user=request.user).all()
    return render(request,'userprofile.html',{'active_tab': 'address','address':address}) 



def changepassword(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    user = request.user
    address = useraddress.objects.filter(user=user).all()
    error=None
    if request.method == 'POST':
        password = request.POST.get('currentpassword')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        print(password,pass1,pass2)
        messages.get_messages(request).used = True
        if not  check_password(password,user.password):
            error='password is  incorrect'
        if pass1!=pass2:
            error='password does not match'
        if error :
            messages.error(request,error)
            return render(request,'userprofile.html',{'active_tab': 'change-password','address':address})
        user.password = make_password(pass1)
        user.save()
        login(request, user)
        print('sucess========================================================================================')
        success = 'the password is changed success'
        messages.success(request,success)
        return render(request,'userprofile.html',{'active_tab': 'change-password','address':address,})

    
    return render(request,'userprofile.html',{'active_tab': 'change-password','address':address})

