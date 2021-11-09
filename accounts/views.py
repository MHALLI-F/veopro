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

from .forms import UserLoginForm


def login_view(request):
    #next= request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        #user=form.save
        username= form.cleaned_data.get('username')
        password= form.cleaned_data.get('password')
        user= authenticate(username=username, password=password)
        if  user is  not  None:
            login(request,user)
            return redirect('/home')
        #user=form.save
        #login(request, user,backend='django.contrib.auth.backends.ModekBackend')
        
        #if next:
         #   return redirect(next)
        #return redirect('/home')
    
    context = {
        'form':form,
    }

    return render(request, "login.html",context)
