from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from user_auth.forms import RegistrationForm, LoginForm
from django.contrib import messages
from core.models import User
from django.conf import settings
from django.core.mail import send_mail
import requests
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# 'Courier New', monospace
# Create your views here.

def google_auth(request):
    # Replace these with your actual Google API credentials
    
    client_id = None
    client_secret = None
    redirect_uri = 'https://ishort.in/auth/google-auth/'

    if 'code' in request.GET:
        # Exchange the code for an access token
        code = request.GET['code']
        token_url = 'https://accounts.google.com/o/oauth2/token'
        token_params = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        token_response = requests.post(token_url, data=token_params)
        token_data = token_response.json()
        access_token = token_data['access_token']

        # Fetch user profile using the access token
        profile_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = requests.get(profile_url, headers=headers)
        profile_data = profile_response.json()

        try:
            custom_user = User.objects.get(email=profile_data['email'])
            # User already exists, update their data
            custom_user.google_id = profile_data['id']
            custom_user.extra_data = profile_data.get('picture', '')
            custom_user.first_name = profile_data.get('given_name', '')
            custom_user.last_name = profile_data.get('family_name', '')
            custom_user.method = "google"
            custom_user.is_email_varified = True
            custom_user.save()
        
        except User.DoesNotExist:
            custom_user = User(email=profile_data['email'])
            custom_user.set_unusable_password()
            custom_user.google_id = profile_data['id']
            custom_user.first_name = profile_data.get('given_name', '')
            custom_user.last_name = profile_data.get('family_name', '')
            custom_user.extra_data = profile_data.get('picture', '')
            custom_user.method = "google"
            custom_user.is_email_varified = True
            custom_user.save()

        login(request, custom_user)
        messages.success(request, f'Hey, {custom_user.email} Successfully logged in using google !')
        return redirect('core:User_Dashboard')

    else:
        # Redirect the user to the Google login page
        auth_url = 'https://accounts.google.com/o/oauth2/auth'
        auth_params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email',
            'response_type': 'code',
        }
        auth_url = f'{auth_url}?{"&".join(f"{key}={val}" for key, val in auth_params.items())}'
        return redirect(auth_url)


def auth_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user_obj = User.objects.filter(email = email).first()

            if not user_obj:
                messages.error(request, f'invalid email {email}')
                return redirect('user_auth:auth_login')

            if not user_obj.is_email_varified:
                messages.warning(request, 'Your email is not verify yet, go to email and verify it first, then try to log in.')
                return redirect('user_auth:auth_login')

            valid_user = authenticate(request, email = email, password = password)
            if not valid_user:
                messages.error(request, 'Incorrect Login credential.')
                return redirect('user_auth:auth_login')

            login(request, valid_user)
            messages.success(request, f'Hey, {email} welcome to your dashboard. we are happy to see you again !')
            return redirect('core:User_Dashboard')
            
    else:
        form = LoginForm()
    
    context = {
        'form':form
    }
    return render(request, 'login.html', context)

def auth_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_auth:Verify_account')
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'register.html', context)

def verification_msg(request):
    return render(request, 'verification_email_sent.html')

def user_email_verify(request, slug):
    user_obj = User.objects.filter(email_token = slug).first()
    if not user_obj:
        messages.error(request, 'Oops, Email token expired. try to regenerate it !')
        return redirect('user_auth:auth_login')

    user_obj.is_email_varified = True
    user_obj.save()
    return render(request, 'verification_success.html')

def reset_pass_email(request):
    if request.method == "POST":
        email = request.POST['email']

        if not User.objects.filter(email = email).first():
            messages.error(request, 'Your email does not contain any user account. please enter a valid email')
            return redirect('user_auth:reset_pass_email')

        user_obj = User.objects.get(email = email)
        email_token = user_obj.email_token
        send_email_after_forgotpassword(email, email_token)
        messages.success(request, f'Hey, {email} a password reset link sent to your account. please go to your email and reset password now.')
        return redirect('user_auth:reset_pass_email')
    
    return render(request, 'reset_pass_email.html')

# def send_email_after_forgotpassword(email, email_token):
#     subject = 'Reset your password'
#     message = f'Hii, Press the link to reset your password http://localhost:8000/auth/reset/password/{email_token}'
#     from_email = settings.EMAIL_HOST_USER
#     recipient_list = [email]
#     send_mail(subject, message, from_email, recipient_list)

def send_email_after_forgotpassword(email, email_token):
    subject = 'Reset your password now !'

    # Render the HTML template and include the user's email
    verification_link = f'https://ishort.in/auth/reset/password/{email_token}'  # Update the link as needed
    html_message = render_to_string('email/reset-password.html', {'verification_link': verification_link, 'user_email': email})

    # Create an EmailMessage with the same HTML content for both HTML and plain text
    email = EmailMessage(
        subject,
        html_message,  # Use the same HTML content for both HTML and plain text
        settings.EMAIL_HOST_USER,
        [email],
    )
    email.content_subtype = 'html'  # Set the content type to HTML
    email.send()

def reset_password(request, slug):
    if request.method == "POST":
        password = request.POST.get('password')
        
        user_obj = User.objects.filter(email_token = slug).first()
        user_obj.set_password(password)
        user_obj.save()
        messages.success(request, 'Password reset Done. Try to login with a valid credential !')
        return redirect('user_auth:auth_login')
    return render(request, 'reset_pass.html')

def auth_logout(request):
    email = request.user.email
    logout(request)
    messages.warning(request, f"{email}, thanks for spending some moment with us!")
    return redirect('user_auth:auth_login')
