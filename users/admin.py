from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# from .forms import CustomUserRegistrationForm, EmailAuthenticationForm

# @admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # add_form = CustomUserRegistrationForm
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional info', {'fields': ('is_verified', 'address_line_1', 'address_line_2', 'city', 'postcode', 'country', 'mobile', 'profile_picture')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

# Register the CustomUserAdmin with the default admin site
admin.site.register(CustomUser, CustomUserAdmin)

# Override the default admin login form
# admin.site.login_form = EmailAuthenticationForm
