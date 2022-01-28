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
from VEO.views import filterDosT,filterDosAT,TrDosT,TrImmatT,TrDsinT,TrDcrT,TrTypeT,TrStatT,TrExpT,TrIAdvT,TrRFT,TrStatDouteT,TrobsT , TrDosIT,TrImmatIT,TrDsinIT,TrDcrIT,TrTypeIT,TrStatIT,TrExpIT,TrIAdvIT,TrRFIT,TrStatDouteIT,TrobsIT,  dossierstrait, inis, search, err, Rate,details,filterDos, filtre, observation, dossiersAtrait, TrDosAT,TrImmatAT,TrDsinAT,TrDcrAT,TrTypeAT,TrStatAT,TrExpAT,TrIAdvAT,TrRFAT,TrStatDouteAT,TrobsAT , TrDosIAT,TrImmatIAT,TrDsinIAT,TrDcrIAT,TrTypeIAT,TrStatIAT,TrExpIAT,TrIAdvIAT,TrRFIAT,TrStatDouteIAT,TrobsIAT, TrDos,TrImmat,TrDsin,TrDcr,TrType,TrStat,TrExp,TrIAdv,TrRF,TrStatDoute,Trobs , TrDosI,TrImmatI,TrDsinI,TrDcrI,TrTypeI,TrStatI,TrExpI,TrIAdvI,TrRFI,TrStatDouteI,TrobsI


from accounts.views import login_view ,deconnexion
#pour que  les  images  s'affiches
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),   
    path('home/', inis,name="inis"),
    path('search/',search,name="search"),
    path('details/<str:Dossier>/',details,name="details"),
    path('filtre/',filtre,name="filtre"),

     #path('statutdoute/',statutdoute,name="statutdoute"),
   #path('details$',details,name="details$"),
    path('dt/',dossiersAtrait,name="dossiersAtrait"),
    path('dtraités/',dossierstrait,name="dossierstrait"),
    path('filterDos/',filterDos,name="filterDos"),
    path('filterDosAT/',filterDosAT,name="filterDosAT"),
    path('filterDosT/',filterDosT,name="filterDosT"),
   # path('filterimmat/',filterimmat,name="filterimmat"),
    path('home/login/', login_view),
    path('login/', login_view),
    path('logout/', deconnexion),
    path('search/err/',err,name="err"),
    path('search/err/home',inis,name="inis"),
    path('search/err/login/',login_view),
    path('search/login/',login_view),
    path('observation/',observation,name="observation"),

    path('TrDos/',TrDos,name="TrDos"),
    path('TrImmat/',TrImmat,name="TrImmat"),
    path('TrDsin/',TrDsin,name="TrDsin"),
    path('TrDcr/',TrDcr,name="TrDcr"),
    path('TrType/',TrType,name="TrType"),
    path('TrStat/',TrStat,name="TrStat"),
    path('TrExp/',TrExp,name="TrExp"),
    path('TrIAdv/',TrIAdv,name="TrIAdv"),
    path('TrRF/',TrRF,name="TrRF"),
    path('TrStatDoute/',TrStatDoute,name="TrStatDoute"),
    path('Trobs/',Trobs,name="Trobs"),
    path('TrDosI/',TrDosI,name="TrDosI"),
    path('TrImmatI/',TrImmatI,name="TrImmatI"),
    path('TrDsinI/',TrDsinI,name="TrDsinI"),
    path('TrDcrI/',TrDcrI,name="TrDcrI"),
    path('TrTypeI/',TrTypeI,name="TrTypeI"),
    path('TrStatI/',TrStatI,name="TrStatI"),
    path('TrExpI/',TrExpI,name="TrExpI"),
    path('TrIAdvI/',TrIAdvI,name="TrIAdvI"),
    path('TrRFI/',TrRFI,name="TrRFI"),
    path('TrStatDouteI/',TrStatDouteI,name="TrStatDouteI"),
    path('TrobsI/',TrobsI,name="TrobsI"),
    
    path('TrDosT/',TrDosT,name="TrDosT"),
    path('TrImmatT/',TrImmatT,name="TrImmatT"),
    path('TrDsinT/',TrDsinT,name="TrDsinT"),
    path('TrDcrT/',TrDcrT,name="TrDcrT"),
    path('TrTypeT/',TrTypeT,name="TrTypeT"),
    path('TrStatT/',TrStatT,name="TrStatT"),
    path('TrExpT/',TrExpT,name="TrExpT"),
    path('TrIAdvT/',TrIAdvT,name="TrIAdvT"),
    path('TrRFT/',TrRFT,name="TrRFT"),
    path('TrStatDouteT/',TrStatDouteT,name="TrStatDouteT"),
    path('TrobsT/',TrobsT,name="TrobsT"),
    path('TrDosIT/',TrDosIT,name="TrDosIT"),
    path('TrImmatIT/',TrImmatIT,name="TrImmatIT"),
    path('TrDsinIT/',TrDsinIT,name="TrDsinIT"),
    path('TrDcrIT/',TrDcrIT,name="TrDcrIT"),
    path('TrTypeIT/',TrTypeIT,name="TrTypeIT"),
    path('TrStatIT/',TrStatT,name="TrStatIT"),
    path('TrExpIT/',TrExpIT,name="TrExpIT"),
    path('TrIAdvIT/',TrIAdvIT,name="TrIAdvIT"),
    path('TrRFIT/',TrRFIT,name="TrRFIT"),
    path('TrStatDouteIT/',TrStatDouteIT,name="TrStatDouteIT"),
    path('TrobsIT/',TrobsIT,name="TrobsIT"),


    path('TrDosAT/',TrDosAT,name="TrDosAT"),
    path('TrImmatAT/',TrImmatAT,name="TrImmatAT"),
    path('TrDsinAT/',TrDsinAT,name="TrDsinAT"),
    path('TrDcrAT/',TrDcrAT,name="TrDcrAT"),
    path('TrTypeAT/',TrTypeAT,name="TrTypeAT"),
    path('TrStatAT/',TrStatAT,name="TrStatAT"),
    path('TrExpAT/',TrExpAT,name="TrExpAT"),
    path('TrIAdvAT/',TrIAdvAT,name="TrIAdvAT"),
    path('TrRFAT/',TrRFAT,name="TrRFAT"),
    path('TrStatDouteAT/',TrStatDouteAT,name="TrStatDouteAT"),
    path('TrobsAT/',TrobsAT,name="TrobsAT"),
    path('TrDosIAT/',TrDosIAT,name="TrDosIAT"),
    path('TrImmatIAT/',TrImmatIAT,name="TrImmatIAT"),
    path('TrDsinIAT/',TrDsinIAT,name="TrDsinIAT"),
    path('TrDcrIAT/',TrDcrIAT,name="TrDcrIAT"),
    path('TrTypeIAT/',TrTypeIAT,name="TrTypeIAT"),
    path('TrStatIAT/',TrStatIAT,name="TrStatIAT"),
    path('TrExpIAT/',TrExpIAT,name="TrExpIAT"),
    path('TrIAdvIAT/',TrIAdvIAT,name="TrIAdvIAT"),
    path('TrRFIAT/',TrRFIAT,name="TrRFIAT"),
    path('TrStatDouteIAT/',TrStatDouteIAT,name="TrStatDouteIAT"),
    path('TrobsIAT/',TrobsIAT,name="TrobsIAT"),
    #path('', include("django.contrib.auth.urls")),
    path('', login_view),
 
   
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#+static   pour  les images

