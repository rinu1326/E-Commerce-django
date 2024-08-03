from django.shortcuts import render,redirect
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode


from django.core.mail import EmailMessage
from django.conf import settings
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate,login,logout


# Create your views here.



def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']
        
        if password != confirm_password:
            messages.warning(request, "Passwords do not match")
            return render(request, "signup.html")
        
        try:
            if User.objects.get(username=email):
                messages.warning(request, "Email is already taken")
                return render(request, "signup.html")
        except ObjectDoesNotExist:
            pass

        user = User.objects.create_user(email,email,password)
        user.save()

        # Optionally, send an activation email here
        # ...

        messages.success(request, "Account created successfully. Please log in.")
        return redirect('/auth/login')
    
    return render(request, "signup.html")
    
def handlelogin(request):
    if request.method == 'POST':
        username = request.POST['email']
        userpassword = request.POST['pass1']
        myuser = authenticate(username=username, password=userpassword)

        if myuser is not None:
            login(request, myuser)
            messages.success(request, 'Login Success')
            return redirect('/')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('/auth/login')
    return render(request, 'login.html')  # Assuming 'login.html' is the correct template for login


def handlelogout(request):
    logout(request)
    messages.info(request,"Logout Success")
    return redirect('/auth/login')
