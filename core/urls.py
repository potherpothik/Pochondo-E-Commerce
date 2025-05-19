from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('store-locator/', views.store_locator, name='store_locator'),
    path('delivery-policy/', views.delivery_policy, name='delivery_policy'),
    path('exchange-policy/', views.exchange_policy, name='exchange_policy'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('safety-advisory/', views.safety_advisory, name='safety_advisory'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
]