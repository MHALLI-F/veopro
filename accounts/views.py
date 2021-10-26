from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render


from django import forms
from django.contrib.auth import (
    authenticate,
     get_user_model,
     login,
     logout
     )

from .forms import (UserLoginForm, UserRegisterForm)

def login_view(request):
    next= request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username= form.cleaned_data.get('username')
        password= form.cleaned_data.get('pasword')
        user= authenticate(username=username, password=password)
        login( request, user)
        if next:
            return redirect(next)
        return redirect('/home')
    
    context = {
        'form':form,
    }

    return render(request, "login.html",context)