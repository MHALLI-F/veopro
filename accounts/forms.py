from django import forms
from django.forms import ModelForm
from django.contrib.auth import (authenticate, get_user_model)

#User = get_user_model()

class UserLoginForm(forms.Form):
    

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Cet utilisateur n'existe pas")
            if not user.check_password(password):
                raise forms.ValidationError('Mot de passe incorrect')
            if not user.is_active:
                raise forms.ValidationError("Cet utilisateur n'est pas actif")
        return super(UserLoginForm, self).clean(*args, **kwargs)



