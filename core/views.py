from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')

def contact(request):
    return render(request, 'core/contact.html')

def about(request):
    return render(request, 'core/about.html')

def store_locator(request):
    return render(request, 'core/store_locator.html')

def delivery_policy(request):
    return render(request, 'core/delivery_policy.html')

def exchange_policy(request):
    return render(request, 'core/exchange_policy.html')

def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')

def safety_advisory(request):
    return render(request, 'core/safety_advisory.html')

def terms_conditions(request):
    return render(request, 'core/terms_conditions.html')