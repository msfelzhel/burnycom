
from django import forms
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from users.models import User

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget= forms.TextInput(attrs= {"autofocus":True,
                                'class' : 'form-control border-0',
                                }))
    password = forms.CharField(
        widget= forms.PasswordInput(attrs= {"autocomplete":"current-password",
                                'class' : 'form-control pr-11 border-0',
                                }))
    
    
    class Meta:
        model = User()
        fields = ['username','password']




class UserRegistrationForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password1",
            "password2",
 
        )
email = forms.CharField()
username = forms.CharField()
first_name = forms.CharField()
last_name = forms.CharField()
password1 = forms.CharField()
password2 = forms.CharField()