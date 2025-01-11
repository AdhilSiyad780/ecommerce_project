from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
import random
import sweetify
from django.contrib.auth import authenticate, login, logout
from datetime import timedelta
from django.core.mail import send_mail
from .models import OTP,Refferal
from Catagory.models import catagory
from django.contrib import messages
from products.models import Products
from django.contrib.auth.hashers import make_password
from Coupons.models import wallet
from transaction.models import transactions
from django.utils.crypto import get_random_string
import re



# Create your views here.




def otp_generetor():
    return random.randint(100000,999999)

def send_otp_mail(otp,email):
    print(otp)
    try:
        message = 'OTP to login'
        subject = f'you otp to login is {otp}'
        send_mail(
        message,subject,'adhilziyad780@gmail.com',[email])
        return True

    except Exception as e:
        return False
    


def signup(request):
    if  request.user.is_authenticated:
        return redirect('index')
    error = {}
    theerror = ''
    if request.method =='POST':
        username = request.POST.get('uname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        refferal = request.POST.get('Refferal',None)
        if not username:
            theerror = 'username is manditory'
        elif len(username)<=8:
            theerror = 'the username should be greater than 8 charactors'
        elif User.objects.filter(username=username).exists():
            theerror = 'the username already exists'
        elif username.strip()== '' :
            theerror = 'username cannot be whitespace'
        if theerror:
            return render(request,'signup.html',{'username':username,'usererror':theerror} )
        
        
        elif not email:
            theerror='email is manditory'
        elif User.objects.filter(email=email).exists():
            theerror='The email already exists'
        elif len(email)<9:
            theerror = 'Enter a valid email'
        elif email.strip()== '' :
            theerror = 'email cannot be whitespace'
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            error = 'Enter a valid email address.'
        if theerror:
            return render(request,'signup.html',{'username':username,'email':email,'emailerror':theerror} )
        

        elif len(pass1) < 8:
            theerror = 'Password must be at least 8 characters long.'
        elif not any(char.isupper() for char in pass1):
            theerror = 'Password must contain at least one uppercase letter.'
        elif not any(char.islower() for char in pass1):
            theerror = 'Password must contain at least one lowercase letter.'
        elif not any(char.isdigit() for char in pass1):
            theerror = 'Password must contain at least one digit.'
        elif not any(char in "!@#$%^&*()_" for char in pass1):
            theerror = 'Password must contain at least one special character.'
        elif pass1!=pass2:
            theerror = 'your passwords does not match'
        if theerror:
            return render(request,'signup.html',{'username':username,'email':email,'passerror':theerror} )
        
        if refferal and not Refferal.objects.filter(refferal_code=refferal).exists():
            theerror = 'invalid Refferal code'
        if theerror:
            return render(request,'signup.html',{'username':username,'email':email,'refererror':theerror})
        

        
        
         

    

        #password=================================validation
        # usernaem ================================ validation 
        try:
            print('==========================================================aign')
            otp = otp_generetor()
            expiry_time = timezone.now()+ timedelta(seconds=60)
            print(otp,expiry_time)
            

            OTP.objects.update_or_create(email=email,defaults={'otp': otp, 'expires_at': expiry_time})
            error = {}
            
            request.session['registration'] = {'username':username,'email':email,'password':pass1 ,'Refferal':refferal}

            
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

                user = User.objects.create_user(username=registration['username']
                                                ,email=registration['email']
                                                ,password=registration['password'])
            
                user.save()
                login(request,user)
                refferal_code=get_random_string(10).upper()
                for val in range(1,30):
                    if Refferal.objects.filter(refferal_code=refferal_code).exists():
                        print('=================this refferal code already exist')
                        refferal_code = get_random_string(10)
                    break

                ref=Refferal.objects.create(user=request.user,refferal_code=refferal_code)
                print('=================referal created')
                ref.save()




                otp_real.delete()
                reffer = registration['Refferal']
                print(reffer,'==================refferal code=========================================================')
                if reffer:
                    try:
                        print('11111111111111111111111111111111111111111111111111111111111111111111111111111111111')
                        reffered_by_user_at = get_object_or_404(Refferal,refferal_code=reffer)
                        reffered_by_user= reffered_by_user_at.user
                        ref.reffered_by=reffered_by_user
                        ref.save()

                        print("22222222222222222222222222222222222222222222222222222222222222222222222222222")
                        alwallet,created = wallet.objects.get_or_create(user=reffered_by_user)
                        if not created:
                            alwallet.balance += 100
                            print(f'{alwallet.user} has incerased 100')
                            transactions.objects.create(user=reffered_by_user,status='Refferal',amount=100)
                        else:
                            alwallet.balance+=100
                            transactions.objects.create(user=reffered_by_user,status='Refferal',amount=100)
                            alwallet.save()

                        wallet.objects.create(user=request.user,balance=100)
                        
                        transactions.objects.create(user=request.user,status='Refferal',amount=100)


                        
                    except Refferal.DoesNotExist:
                        print('==============================error when refferal')
                        pass

                del request.session['registration']
                

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
    if  request.user.is_authenticated:
        return redirect('index')
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
    alpha = catagory.objects.filter(is_active=True)
    arrivals = Products.objects.filter(is_active=True,catagory__is_active=True).order_by('-id')[:4]
    Product6 = Products.objects.filter(is_active=True,catagory__is_active=True).all()[:6]
    return render(request,'index.html',{'item':alpha,'newarrivals':arrivals,'product6':Product6})

def logout_user(request):
    logout(request)
    return redirect('login_user')

def forgot_password(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    print('=======================1==============1=========1============1================')
    
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