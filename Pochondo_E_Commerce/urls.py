from django.contrib import admin
from django.urls import include, path
# from social_django.views import GoogleOAuth2View, FacebookOAuth2View
# from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
# from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
# from allauth.socialaccount.providers.oauth2.views import OAuth2View

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('wishlist/', include('wishlist.urls', namespace='wishlist')),
    path('users/', include('users.urls', namespace='users')),
    path('products/', include('products.urls', namespace='products')),
    path('users/', include('users.urls', namespace='users')),
    path('orders/', include('orders.urls', namespace='orders')),
    # path('accounts/', include('allauth.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    # path('accounts/google/login/', GoogleOAuth2View.as_view(), name='google_login'),
    # path('accounts/facebook/login/', FacebookOAuth2View.as_view(), name='facebook_login'),
    # path('accounts/google/login/', OAuth2View.adapter_view(GoogleOAuth2Adapter), name='google_login'),
    # path('accounts/facebook/login/', OAuth2View.adapter_view(FacebookOAuth2Adapter), name='facebook_login'),
    path('products/', include('products.urls', namespace='products')),
]
