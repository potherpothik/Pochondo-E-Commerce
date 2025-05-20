from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
# import random
from .models import CustomUser

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False  # User will be inactive until email verification
                user.save()
                
                # Send verification email
                send_verification_email(request, user)
                
                messages.success(request, 'Account created successfully. Please check your email to verify your account.')
                return redirect('core:index')
            except IntegrityError:
                messages.error(request, 'An account with this email already exists.')
                return redirect('users:register')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Changed from 'username' to 'email'
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active and user.is_verified:
                login(request, user)
                return redirect('core:index')
            elif not user.is_verified:
                messages.error(request, 'Please verify your email address before logging in.')
                return redirect('users:login')
            else:
                messages.error(request, 'Your account is inactive. Please contact support.')
                return redirect('users:login')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('users:login')
    
    return render(request, 'users/login.html') 

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Handle form submission
        # Update user profile
        messages.success(request, 'Profile updated successfully.')
        return redirect('users:profile')
    return render(request, 'users/edit_profile.html')

def otp_verification(request):
    if request.method == 'POST':
        # Verify OTP
        return redirect('core:index')
    return render(request, 'users/otp.html')

def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Logic to resend verification email
        messages.success(request, 'Verification email has been resent. Please check your inbox.')
        return redirect('users:login')
    return render(request, 'users/resend_verification.html')

@login_required
def privacy_settings(request):
    if request.method == 'POST':
        # Update privacy settings
        messages.success(request, 'Privacy settings updated successfully.')
        return redirect('users:profile')
    return render(request, 'users/privacy_settings.html')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        # Send account deletion email
        send_account_deletion_email(user)
        # Schedule account for deletion or delete immediately
        messages.success(request, 'Your account has been scheduled for deletion.')
        return redirect('products:home')
    return render(request, 'users/delete_account.html')

# Helper functions for email sending
# def send_verification_email(request, user):
#     """Send verification email to user"""
#     verification_url = f"{request.scheme}://{request.get_host()}/users/verify/{user.id}/"
#     context = {
#         'user': user,
#         'verification_url': verification_url
#     }
#     email_html = render_to_string('users/verification_email.html', context)
#     send_mail(
#         'Verify Your Email Address',
#         'Please verify your email address',
#         settings.DEFAULT_FROM_EMAIL,
#         [user.email],
#         html_message=email_html,
#         fail_silently=False,
#     )

def send_verification_email(request, user):
    """Send verification email with token-based link"""
    # Generate unique verification token
    verification_token = get_random_string(50)
    
    # Store token and timestamp in user model
    user.email_verification_token = verification_token
    user.token_created_at = timezone.now()
    user.save()

    # Build verification URL with token
    verification_url = f"{request.scheme}://{request.get_host()}/users/verify/{verification_token}/"
    
    # Email context
    context = {
        'user': user,
        'verification_url': verification_url,
        'support_email': settings.SUPPORT_EMAIL,
        'privacy_policy_url': f"{request.scheme}://{request.get_host()}/privacy-policy/",
        'expiration_hours': 24  # Token valid for 24 hours
    }

    # Render and send email
    email_html = render_to_string('users/verification_email.html', context)
    send_mail(
        'Verify Your Email Address - POCHONDO',
        strip_tags(email_html),  # Plain text version
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=email_html,
        fail_silently=False,
    )

def send_account_deletion_email(user):
    """Send account deletion notification email"""
    deletion_date = timezone.now() + timezone.timedelta(days=14)  # 14 days grace period
    context = {
        'user': user,
        'deletion_date': deletion_date
    }
    email_html = render_to_string('users/account_deletion_email.html', context)
    send_mail(
        'Account Deletion Request',
        'Your account is scheduled for deletion',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=email_html,
        fail_silently=False,
    )

def send_password_change_notification(user):
    """Send password change notification email"""
    context = {
        'user': user,
        'change_time': timezone.now()
    }
    email_html = render_to_string('users/password_change_notification.html', context)
    send_mail(
        'Password Change Notification',
        'Your password has been changed',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=email_html,
        fail_silently=False,
    )

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('core:index')

def password_reset_done(request):
    # Function logic with the redirect at the end
    return redirect('core:index')  

def dashboard(request):
    return render(request, 'users/dashboard.html')

# def verify_email(request, verification_token):
#     try:
#         user = CustomUser.objects.get(email_verification_token=verification_token)
#         if not user.is_verified:
#             user.is_verified = True
#             user.is_active = True
#             user.email_verification_token = None  # Clear the token after verification
#             user.save()
#             messages.success(request, 'Your email has been verified. You can now login.')
#         else:
#             messages.info(request, 'Your email is already verified.')
#     except CustomUser.DoesNotExist:
#         messages.error(request, 'Invalid verification link.')
    
#     return redirect('users:login')

def send_verification_email(request, user):
    """Send verification email to user"""
    verification_url = f"{request.scheme}://{request.get_host()}/users/verify/{user.id}/"
    context = {
        'user': user,
        'verification_url': verification_url
    }
    email_html = render_to_string('users/verification_email.html', context)
    try:
        send_mail(
            'Verify Your Email Address',
            'Please verify your email address',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=email_html,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")


def verify_email(request, verification_token):
    try:
        user = CustomUser.objects.get(id=verification_token)
        
        # Check token expiration (24 hours)
        # if (timezone.now() - user.token_created_at).total_seconds() > 86400:  # 24*60*60
        #     messages.error(request, 'Verification link has expired.')
        #     return redirect('users:resend_verification')
            
        if not user.is_verified:
            user.is_verified = True
            user.is_active = True
            user.email_verification_token = None  # Clear used token
            user.save()
            messages.success(request, 'Email verified successfully! You can now login.')
        else:
            messages.info(request, 'Email is already verified.')
            
    except CustomUser.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
    
    return redirect('users:login')