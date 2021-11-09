"""VEOsmart URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path,include
from VEO.views import inis,statutdoute, search, err, Rate,details, filtre, observation


from accounts.views import login_view
#pour que  les  images  s'affiches
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),   
    path('home/', inis,name="inis"),
    path('search/',search,name="search"),
    path('details/<str:Dossier>/',details,name="details"),
    path('filtre/',filtre,name="filtre"),
    path('statutdoute/',statutdoute,name="statutdoute"),
   #path('details$',details,name="details$"),
 
    path('home/login/', login_view),

    path('search/err/',err,name="err"),
    path('search/err/home',inis,name="inis"),
    path('search/err/login/',login_view),
    path('search/login/',login_view),
    path('observation/',observation,name="observation"),



    #path('', include("django.contrib.auth.urls")),
    path('', login_view),
 
   
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#+static   pour  les images

