
from django.contrib import admin
from django.db import models
from .models import Veodata, Assistance, Bris_De_Glace, Veoservices, veotest
from accounts.forms import UserLoginForm
# Register your models here.
admin.site.site_header ='VEOsmart Admin'
class VeoAdmin(admin.ModelAdmin):
    lidt_display=('title', 'font_size')
    list_filer=('created',)
            
    change_lidt_template='admin/base_site.html'
    font_size= models.IntegerField()
    #admin.site.register(UserLoginForm)                
                   
    admin.site.register(Veodata)
    admin.site.register(Assistance)
    admin.site.register(veotest)
                    
                    
    admin.site.register(Bris_De_Glace)
    admin.site.register(Veoservices)
                    #admin.site.register(detailField, VeoAdmin)# Register your models here.
