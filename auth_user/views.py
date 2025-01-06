from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.utils import timezone
import random
import sweetify
from django.contrib.auth import authenticate, login, logout
from datetime import timedelta
from django.core.mail import send_mail
from .models import OTP
from Catagory.models import catagory
from django.contrib import messages
from products.models import Products
from django.contrib.auth.hashers import make_password


# Create your views here.




def otp_generetor():
    return random.randint(100000,999999)

def send_otp_mail(otp,email):
    try:
        message = 'OTP to login'
        subject = f'you otp to login is {otp}'
        send_mail(
        message,subject,'adhilziyad780@gmail.com',[email])
        return True

    except Exception as e:
        return False
    


def signup(request):
    error = {}
    theerror = ''
    if request.method =='POST':
        username = request.POST.get('uname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        

        if User.objects.filter(username=username).exists():
            theerror = 'username already exists'
            return render(request,'signup.html',{ 'usererror':theerror})
        
        if User.objects.filter(email=email).exists():
            theerror = 'email already exists'
            return render(request,'signup.html',{ 'emailerror':theerror})
        if pass1!=pass2:
            theerror = 'password does not match'
            return render(request,'signup.html',{ 'passerror':theerror})


    

        #password=================================validation
        # usernaem ================================ validation 
        try:
            print('==========================================================aign')
            otp = otp_generetor()
            expiry_time = timezone.now()+ timedelta(seconds=60)
            print(otp,expiry_time)
            

            OTP.objects.update_or_create(email=email,defaults={'otp': otp, 'expires_at': expiry_time})
            error = {}
            
            request.session['registration'] = {'username':username,'email':email,'password':pass1 }

            
            if not send_otp_mail(otp,email):
                error['email'] = 'failed to send otp to your email.Please try again'
                return render(request,'signup.html',{'error':error, 'username':username,'email':email})
            

            return redirect('verify_otp',email=email)
            #+f'?email={email}&otp={otp}'
        except Exception as e:

            print(f'{e}==============')
            error=e
            return render(request,'signup.html',{'error':error})
    return render(request,'signup.html')
        
def verify_otp(request, email):
    try:
        print('=====================================================================================1')
        registration = request.session['registration']
    except KeyError:
        return render(request,'otp.html',{'error':'An unexpected error occured','email':email})
    if not registration:
        return render(request,'otp.html',{'error':'A unexpected error'})
    
    if request.method=='POST':
        print('=====================================================================================post')

        enter_otp = request.POST.get('otp')
        print(enter_otp)
        try:
            otp_real = OTP.objects.get(email=email)
            beta = timezone.now()
            gama = timedelta(seconds=60)
            
            if beta > otp_real.created_at + gama:
                return render(request, 'otp.html', {
                    'error': 'OTP has expired. Please request a new one.',
                    'email': email
                })
            if str(otp_real.otp)==enter_otp:

                user = User.objects.create_user(username=registration['username'],email=registration['email'],password=registration['password'])
                user.save()

                otp_real.delete()
                del request.session['registration']
                login(request,user)

                return redirect('index')
            else:
                return render(request,'otp.html',{'error':'your otp does not match','email':email})
                

        except OTP.DoesNotExist as e:
            return render(request,'otp.html',{'error': e,'email':email})
        
        
    
        
    return render(request,'otp.html',{'email':email})
   
def resend_otp(request,email):
    print(email)
    
    try:
   
        alpha = OTP.objects.get(email=email)    
        beta = timedelta(seconds=60)
        sampel = alpha.expires_at
        gama = timezone.now()
        print(sampel)
        sample = alpha.created_at
        
        # print(alpha.expires_at,'=============================================')

        
        if gama > alpha.created_at+ beta:

        
            alpha.delete()
            otp = otp_generetor()
            sample = timezone.now()+ timedelta(seconds=60)

            expiry_time = sample.strftime('%Y-%m-%d %H:%M:%S')  

            print(otp,email)
            OTP.objects.update_or_create(email=email,defaults={'otp': otp, 'expires_at': expiry_time})
            send_otp_mail(otp,email)
       

        countdown  = 60
        print(countdown)
        print('==============================================================')
        return render(request,'otp.html',{'email':email,'countdown':countdown})

            
    # except Exception as e:
    #     print(e)
    #     error='some unexpected error occured'
        return render(request,'otp.html',{'error':error,'email':email})
    except OTP.DoesNotExist:
        error = 'otp does not exist'
        return render(request,'otp.html',{'error':error,'email':email})
       
        


def login_user(request):
    error = ' '
    if request.method == "POST":
        username = request.POST.get('email')
        pass1 = request.POST.get('pass')
        
        
        user = authenticate(request,username=username,password=pass1)
        print(username,pass1)

        if user:
            login(request,user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid credentials, please try again.')
            return render(request,'login.html')
            
    return render(request,'login.html')
def home(request):
    alpha = catagory.objects.all()
    arrivals = Products.objects.order_by('-id')[:4]
    Product6 = Products.objects.all()[:6]
    return render(request,'index.html',{'item':alpha,'newarrivals':arrivals,'product6':Product6})

def logout_user(request):
    logout(request)
    return redirect('login_user')

def forgot_password(request):
    print('=======================1==============1=========1============1================')
    if request.user.is_authenticated:
        return redirect('index')
    if request.method=='POST':
        print('=================2==========2===========2=============2===========')
        email = request.POST.get('email') 
        print(email)
        if not User.objects.filter(email=email).exists():
            messages.error(request,'Enter a valid Email')  
            return render(request,'forgotpassword.html')
        
        if not email:
            messages.error(request,'Enter a valid Email')  
            return render(request,'forgotpassword.html')
        otp = otp_generetor()
        expiry_time = timezone.now()+ timedelta(seconds=60)
        OTP.objects.update_or_create(
                                    email=email,
                                    defaults={'otp': otp, 'expires_at': expiry_time}
)

        if not send_otp_mail(otp,email):
            messages.error(request,'Failed to send otp to your email')
            return render(request,'forgotpassword.html')
        return redirect('verify_reset_otp',email=email)
        

    return render(request,'forgotpassword.html')

def verify_reset_otp(request,email):
    alpha = OTP.objects.filter(email=email).first()
    
    if not alpha:
        error='otp not found for this provided email'
        messages.error(request, 'No OTP found for this email.')
        return render(request, 'otp2.html')
    otp = alpha.otp
    error=None
    print(otp)
    if request.method=='POST':
        print('============3=========3=========3==========3=========3=========')
        newotp = request.POST.get('otp')
        
        if newotp!=otp:
            error='otp does not match'
        if error:
            messages.error(request,error)
            return render(request,'otp2.html')
        if alpha:
            alpha.delete()
        return redirect('verify_password',email=email)
        
    return render(request,'otp2.html')
def  verify_password(request,email):
    error=None
    user = User.objects.filter(email=email).first()
    
    if request.method=='POST':
        password1=request.POST.get('password1')
        password2=request.POST.get('password2')
        if password1!=password2:
            error = 'passwords does not match'
        if error:
            messages.error(request,error)
            return render(request,'conformpassword.html')
        print('=============44==============44==========================4==========4============4==========4===========')
        user.set_password(password2)
        user.save()
        return redirect('login_user')
    return render(request,'conformpassword.html')