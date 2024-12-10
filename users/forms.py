
from django import forms
from django.contrib.auth.forms import AuthenticationForm
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