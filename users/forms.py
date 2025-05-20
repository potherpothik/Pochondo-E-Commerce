# from django import forms
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
# from .models import CustomUser

# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = CustomUser
#         fields = ["email", "first_name", "last_name", "phone", "address", "password1", "password2"]

#     def clean(self):
#         cleaned_data = super().clean()
#         password1 = cleaned_data.get("password1")
#         password2 = cleaned_data.get("password2")
        
#         if password1 and password2 and password1 != password2:
#             self.add_error('password2', "Passwords do not match")
        
#         return cleaned_data

# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = CustomUser
#         fields = ["email", "first_name", "last_name"]

# class EmailAuthenticationForm(AuthenticationForm):
#     username = forms.EmailField(label="Email")


# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from .models import CustomUser
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Submit, Layout

# class CustomUserCreationForm(UserCreationForm):
#     class Meta(UserCreationForm.Meta):
#         model = CustomUser
#         fields = ["email", "first_name", "last_name", "phone", "address"]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_id = 'registrationForm'
#         self.helper.form_method = 'post'
#         self.helper.layout = Layout('email','first_name','last_name','phone','address','password1','password2')
#         self.helper.add_input(Submit('submit', 'Create Account', css_class='btn-dark w-100'))

# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from .models import CustomUser
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Row, Column, Field
# from crispy_bootstrap5.forms import StrictButton

# class CustomUserCreationForm(UserCreationForm):
#     class Meta(UserCreationForm.Meta):
#         model = CustomUser
#         fields = ["email", "first_name", "last_name", "phone", "address"]
#         help_texts = {
#             'password1': None,
#             'password2': None,
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_id = 'registrationForm'
#         self.helper.form_method = 'post'
#         self.helper.layout = Layout(
#             Row(
#                 Column('first_name', css_class='col-md-6'),
#                 Column('last_name', css_class='col-md-6'),
#             ),
#             'email',
#             'phone',
#             'address',
#             Field('password1', css_class='password-field'),
#             Field('password2', css_class='password-field'),
#             StrictButton('Create Account', 
#                         type='submit', 
#                         css_class='btn-dark w-100 py-2',
#                         id='registerBtn')
#         )

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Submit

class CustomUserCreationForm(UserCreationForm):
    agree_terms = forms.BooleanField(
        required=True,
        label="I agree to the Terms and Conditions"
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ["email", "first_name", "last_name", "phone", "address"]
        help_texts = {
            'password1': None,
            'password2': None,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'registrationForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            'email',
            'phone',
            'address',
            Field('password1', css_class='password-field'),
            Field('password2', css_class='password-field'),
            Field('agree_terms', template='users/terms_checkbox.html'),
            Submit('submit', 'Create Account', css_class='btn-dark w-100 py-2')
        )