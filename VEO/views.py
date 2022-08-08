from os import lseek
from django.shortcuts import render, get_object_or_404
from .models import Veodata, Assistance, Bris_De_Glace, Veoservices,veotest
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
import datetime
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.core.serializers import serialize
import json

from django.core.serializers.json import DjangoJSONEncoder




# nettoyage  de  numéro de  chassis
def net_numch(a):
    a=a.replace(' ','').replace('-','').replace('_','').replace(',','').replace('.','').replace('*','')
    return a

def inter_dt(dtV , dtE):
    if (dtV and dtE):
        dtV = datetime.strptime(dtV, "%d/%m/%Y").date()
        dtE = datetime.strptime(dtE, "%d/%m/%Y").date()
        return abs(dtV - dtE).days
def inter_dt2(dtV , dtE):
    if (dtV and dtE):
        dtE = datetime.strptime(dtE, "%d/%m/%Y").date()
        dtV = datetime.strptime(dtV, "%d %b, %Y %H:%M:%S").date()
        return (dtV - dtE).days

################################################################### Nettoyage des immatriculations
#Enlever les zéros de début
def remove_zerostart (val):
    i=0
    while (val.startswith('0') and i<len(val)):
        l=list(val)
        l[0]=''
        i=i+1
        val = ''.join(l)
    return val

#Enlever les "WW" à la fin
def remove_WW(a):
    if a.endswith("WW"):
        a= ''.join(list(a)[0:-2])
        if(a.startswith("WW")):
            return a
        else :
            return "WW"+a
    else:
        return a

#Enlever les zeros après les "WW" de début
def remove_WW0(a):
    if a.startswith("WW0"):
        a=''.join(list(a)[2:])
        a=remove_zerostart(a)
        a="WW"+a
        return a
    else:
        return a

#Enlever le mot "EAD" s'il existe
def remove_EAD(a):
    if (a.startswith("EAD")):
        return ''.join(list(a)[3:])
    else:
        return a

#Ajouter le le zéro après le caractère (B7 ==> B07)
def add_zero(a):
    if (len(a) <= 2 or a != '' or not (a is None)):
        if (a[-1].isdigit() and (not a[-2].isdigit())):
            res=list(a)[0:-1]
            res.append("0")
            res.append(a[-1])
            return ''.join(res)
        else:
            return a
    else:
        return a

#Enlever les imm qui contient que des chiffres ou bien que des caractères
def test(a):
    b=''.join(i for i in a if i.isdigit())
    c=''.join(i for i in a if not (i.isdigit()))
    if ((len(b) == len(a)) or ((len(c) == len(a)))):
        return ""
    else:
        return a


#Preprocessing "Immatriculation" (Appeler toutes les fcts défénies)
def Preprocessing_Imm (a):
    if a!=None:
        a=remove_EAD(a)
        a=a.strip()
        a=a.upper()
        a=a.replace(" ", "")
        a=a.replace("/", "")
        a=a.replace("'", "")
        a=a.replace(".", "")
        a=a.replace('-','')
        a=remove_zerostart(a)
        a=remove_WW(a)
        a=remove_WW0(a)
        if (a != '' and not(a is None)):
            a=add_zero(a)
            a=test(a)
            return a


#Convertir Rate fraude de string to float
def str_to_float(stri):
    if stri == "" or stri == "'0.0'" or stri  == None:
        stri=0.0
    else:
        stri=float(stri)
    return stri


@login_required
def inis(request):
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo, '%d/%m/%Y %H:%M')
   
    NBDAT=nbrDAT()
    list_Veo_recente=[]
    NBD=0
    list_Veoservices=Veoservices.objects.all()
    Rate=0
    for i in list_Veoservices:
        if i.Date_création!=None:
            i.Date_création=datetime.datetime.strptime(i.Date_création, '%d/%m/%Y %H:%M')
            i.RateFraude = str_to_float(i.RateFraude)
        if (i.Statut!= "Changement procédure") and (i.RateFraude not in [0,0.0,None]):
            
            list_Veo_recente.append(i)
            
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"NBDossiers":NBDAT}
    return render(request,"home.html",context)

@login_required
def details(request, Dossier):
    Veo=get_object_or_404(Veoservices,id=Dossier)
    Rate=Veo.RateFraude
    NBD=nbrDAT()
    NBDT=nbrDT()
    R1=Veo.Reg1()[0]
    R1_P=Veo.Reg1()[1]
    R1_A=Veo.Reg1()[2]

    R2=Veo.Reg2()[0]
    R2_DDA=Veo.Reg2()[1]
    R2_DS=Veo.Reg2()[2]

    R3=Veo.Reg3()[0]
    R3_DDA=Veo.Reg3()[1]
    R3_DS=Veo.Reg3()[2]

    R4=Veo.Reg4()[0]
    R4_SP=Veo.Reg4()[1]
    R4_SA=Veo.Reg4()[2]

    R5=Veo.Reg5()[0]
    #Dossier assistance qui à la  date moins  de 7h et plus de 20h
    R5_Assis=Veo.Reg5()[1]

    R6=Veo.Reg6()[0]
    #Les  deux dossiers Assistance qui ne dépassent pas 3 mois
    R6_Assis1=Veo.Reg6()[1]
    R6_Assis2=Veo.Reg6()[2]

    R7=Veo.Reg7()[0]
    R7_P=Veo.Reg7()[1]
    R7_A=Veo.Reg7()[2]

    R9=Veo.Reg9()[0]
    R9_DFP=Veo.Reg9()[1]
    R9_DS=Veo.Reg9()[2]

    R8=Veo.Reg8()

    R10=Veo.Reg10()[0]
    R10_Dos=Veo.Reg10()[1]
    
    R12=Veo.Reg12()[0]
    R12_Dos=Veo.Reg12()[1]

    R11=Veo.Reg11()

    R13=Veo.Reg13()[0]
    R13_Dos=Veo.Reg13()[1]

    R14 =Veo.Reg14()
    # Vérifier si c'est superuser
    if request.user.is_superuser:
        SupUse = True
    else:
        SupUse = False
    context={"SupUse":SupUse, "NBDT":NBDT,"NBDossiers":NBD,"Veo":Veo,"Rate":Rate ,"R1": R1,"R1_P": R1_P, "R1_A":R1_A, "R2":R2, "R2_DDA":R2_DDA, "R2_DS":R2_DS,"R3":R3, "R3_DDA":R3_DDA, "R3_DS":R3_DS, "R4":R4, "R4_SP":R4_SP, "R4_SA":R4_SA,"R5":R5 ,"R5_Assis":R5_Assis ,"R6":R6,"R6_Assis1":R6_Assis1 ,"R6_Assis2":R6_Assis2,"R7":R7,"R7_P":R7_P,"R7_A":R7_A, "R9_DFP":R9_DFP, "R9_DS":R9_DS, "R9":R9,"R8":R8,"R11":R11, "R10_Dos":R10_Dos,"R10":R10 , "R12_Dos":R12_Dos,"R12":R12 , "R13_Dos":R13_Dos,"R13":R13, "R14":R14}

    return render(request,"detail.html",context)
def nbrDAT():
    NBD=0
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo, '%d/%m/%Y %H:%M')
    list_Veoservices=Veoservices.objects.all()
    for i in list_Veoservices:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création, '%d/%m/%Y %H:%M')
            if (((Today_DateVeo-Date_création).days<=5) and i.statutdoute=="Non traité" and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) :
                NBD=NBD+1
    return NBD

def nbrDT():
    list_Veoservices=Veoservices.objects.all()
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo, '%d/%m/%Y %H:%M')
    NBD=0
    for i in list_Veoservices:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création, '%d/%m/%Y %H:%M')
            if ((Today_DateVeo-Date_création).days<=10 and (i.statutdoute=="Doute confirmé" or i.statutdoute=="Doute rejeté")   and i.Statut!="Dossier sans suite" and i.Statut!="Changement de procédure") :
                NBD=NBD+1
    return NBD

def DosAff():
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo,'%d/%m/%Y %H:%M')
    list_Veo_recente=[]
    list_Veoservices=Veoservices.objects.all()

    for i in list_Veoservices:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création,'%d/%m/%Y %H:%M')
            if ((((Today_DateVeo-Date_création).days<=25) and (i.Statut!= "Changement procédure")) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" ) )and i.RateFraude not in [0,"0.0","","'0.0'",0.0,None]:
                list_Veo_recente.append(i)
    return  list_Veo_recente

def DosAT():
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo,'%d/%m/%Y %H:%M')
    list_Veo_recente=[]
    list_Veoservices=Veoservices.objects.all()

    for i in list_Veoservices:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création,'%d/%m/%Y %H:%M')
            if ((((Today_DateVeo-Date_création).days<=25) and (i.Statut!= "Changement procédure")) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" ) )and i.RateFraude not in [0,"0.0","","'0.0'",0.0,0,'0.0',None,'5.0','10.0']:
                list_Veo_recente.append(i)
    return  list_Veo_recente

def DosAffdout():
    list_Veo_recente =[]
    list_Veoservices = Veoservices.objects.all()
    NBD=nbrDAT()
    for i in list_Veoservices:
        if i.statutdoute == "Doute confirmé":
            list_Veo_recente.append(i)
    return  list_Veo_recente
def filtre(request):
    id=request.GET.get('filtre')
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    if (id=="Date_creation"):
        list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    elif (id=="Date_sinistre"):
        list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=True)
    else:
        for i in list_Veo_recente:
            i.RateFraude=str_to_float(i.RateFraude)
        list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
   # paginator = Paginator(list_Veo_recente,9)
   # page = request.GET.get('page')
   # veopg = paginator.get_page(page)
    #veopg.sort(key=lambda r: r.RateFraude,reverse=True)
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": list_Veo_recente}
    return render(request,"home.html",context)
    # Vérifier  si  l'utilisateur  connecter  est  un  admin
def SupUse(request):
    if request.user.is_superuser:
        SupUse = True
    else:
        SupUse = False
    return SupUse

def TrDos(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=1
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente":veopg ,"tri":tri}
    return render(request,"home.html",context)

def TrImmat(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=2
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrDsin(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=3
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrDcr(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=4
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrType(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=5
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrStat(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=6
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrExp(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=7
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrIAdv(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=8
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrRF(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=9
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrStatDoute(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=10
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def Trobs(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=11
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg , "tri":tri}
    return render(request,"home.html",context)


def TrDosI(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=12
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente":veopg, "tri":tri}
    return render(request,"home.html",context)

def TrImmatI(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=13
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrDsinI(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=14
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrDcrI(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=15
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrTypeI(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=16
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrStatI(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=17
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrExpI(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=18
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)

def TrIAdvI(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=19
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)
def TrRFI(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=20
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)
def TrStatDouteI(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=21
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)
def TrobsI(request):
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=22
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)



def TrDosAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=1
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente":veopg ,"tri":tri}
    return render(request,"dossieratrait.html",context)

def TrImmatAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=2
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrDsinAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=3
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrDcrAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=4
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)

def TrTypeAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=5
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrStatAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=6
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrExpAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=7
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)

def TrIAdvAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=8
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrRFAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=9
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrStatDouteAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=10
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrobsAT(request):

    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=11
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg , "tri":tri}
    return render(request,"dossieratrait.html",context)


def TrDosIAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=12
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente":veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)

def TrImmatIAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=13
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrDsinIAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=14
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)

def TrDcrIAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=15
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrTypeIAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=16
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrStatIAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=17
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrExpIAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=18
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)

def TrIAdvIAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=19
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrRFIAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=20
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)
def TrStatDouteIAT(request):
    
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=21
    context={"SupUse":SupUse(request),"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrobsIAT(request):
    list_Veo_recente=DosAT()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=22
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri,"NBDT":NBDT}
    return render(request,"dossieratrait.html",context)


def TrDosT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=1
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrImmatT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=2
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrDsinT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=3
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrDcrT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=4
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrTypeT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=5
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrStatT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=6
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrExpT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=7
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrIAdvT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=8
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrRFT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=9
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrStatDouteT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=10
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrobsT(request):

    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=11
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)


def TrDosIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=12
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrImmatIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=13
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrDsinIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=14
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrDcrIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=15
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrDsinIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=14
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrDcrIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=15
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrTypeIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=16
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrStatIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=17
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrExpIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=18
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrIAdvIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=19
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrRFIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
        
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=20
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrStatDouteIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=21
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrobsIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=22
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrdateIT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r:  r.date_obs,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=24
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrdateT(request):
    list_Veo_recente=DosTAff()
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r:  r.date_obs,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=23
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait.html",context)
@login_required
def filterDos(request):
    list_Veo_recente=[]
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo,'%d/%m/%Y %H:%M')
    NBD=nbrDAT()
    NBDT=nbrDT()
    if request.method=='GET':
        query=request.GET.get('search')
    liste2=list(Veoservices.objects.filter(Dossier__icontains=query))
    liste1=list(Veoservices.objects.filter(Immatriculation__icontains=query))
    if liste1==None:
        liste=liste2
    elif liste2==None:
        liste=liste1
    else:
        liste=liste1+liste2
    for i in liste:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création,'%d/%m/%Y %H:%M')
            if ((Today_DateVeo-Date_création).days<=100) and i.RateFraude not in [0,'0.0',None,'5.0','10.0','15.0'] and i not in list_Veo_recente:
                list_Veo_recente.append(i)
                i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)

    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"NBDossiers":NBD,"NBDT":NBDT}
    return render(request,"home.html",context)
@login_required
def filterDosAT(request):
    list_Veo_recente=[]
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo,'%d/%m/%Y %H:%M')
    NBD=nbrDAT()
    NBDT=nbrDT()
    if request.method=='GET':
        query=request.GET.get('search')
        liste2=list(Veoservices.objects.filter(Dossier__icontains=query))
        liste1=list(Veoservices.objects.filter(Immatriculation__icontains=query))
        if liste1==None:
            liste=liste2
        elif liste2==None:
            liste=liste1
        else:
            liste=liste1+liste2
        for i in liste:
            if i.Date_création!=None:
                Date_création=datetime.datetime.strptime(i.Date_création,'%d/%m/%Y %H:%M')
                if ((Today_DateVeo-Date_création).days<=100):
                    if (i.statutdoute=="Non traité" and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) and i not in list_Veo_recente:
                        list_Veo_recente.append(i)
                        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"NBDossiers":NBD,"NBDT":NBDT}
    return render(request,"dossieratrait.html",context)
@login_required
def filterDosT(request):
    list_Veo_recente=[]
    NBD=nbrDAT()
    NBDT=nbrDT()
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo,'%d/%m/%Y %H:%M')
    if request.method=='GET':
        query=request.GET.get('search')
        liste2=list(Veoservices.objects.filter(Dossier__icontains=query))
        liste1=list(Veoservices.objects.filter(Immatriculation__icontains=query))
        if liste1==None:
            liste=liste2
        elif liste2==None:
            liste=liste1
        else:
            liste=liste1+liste2
        for i in liste:
            if i.Date_création!=None:
                Date_création=datetime.datetime.strptime(i.Date_création,'%d/%m/%Y %H:%M')
                if ((Today_DateVeo-Date_création).days<=100):
                    if (i.statutdoute=="Doute confirmé" or i.statutdoute=="Doute rejeté") and i.Statut!="Changement de procédure" and  i.Statut!="Dossier sans suite" and i.RateFraude not in [0,'0.0',None,'5.0','10.0'] and i not in list_Veo_recente:
                        list_Veo_recente.append(i)
                        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)

    
    Veoservice=Veoservices.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT}
    return render(request,"dossiertrait.html",context)

@login_required
def dossierstrait(request):
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente=[]
    list_Veoservices=DosTAff()
    Veoservice=Veoservices.objects.all()
    for i in list_Veoservices:
        if (i.statutdoute=="Doute confirmé" or i.statutdoute=="Doute rejeté") and i.Statut!="Changement de procédure" and  i.Statut!="Dossier sans suite" :
            i.RateFraude = str_to_float(i.RateFraude)
            list_Veo_recente.append(i)

    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)

    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT}
    return render(request,"dossiertrait.html",context)
@login_required
def dossiersAtrait(request):
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente=[]
    list_inst=[]
    list_Veoservices=DosAff()
    list_Veoservicesall= Veoservices.objects.all()
    for i in list_Veoservicesall:
        if i.Statut =="Dossier en instruction" and "D" in i.Dossier:
            list_inst.append(i)
    for i in list_Veoservices:
        
        if (i.statutdoute=="Non traité" and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) :
            i.RateFraude = str_to_float(i.RateFraude)
            list_Veo_recente.append(i)


    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
   # veopg.sort(key=lambda r: r.RateFraude,reverse=True)
   
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"NBDossiers":NBD,"NBDT":NBDT ,"list_inst": list_inst}
    return render(request,"dossieratrait.html",context) 

def DosTAff():
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo,'%d/%m/%Y %H:%M')
    list_Veo_recente=[]
    list_Veoservices=Veoservices.objects.all()

    for i in list_Veoservices:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création,'%d/%m/%Y %H:%M')
            if ((Today_DateVeo-Date_création).days<=8) and (i.Statut!= "Changement procédure") and  (i.statutdoute=="Doute confirmé" or i.statutdoute=="Doute rejeté"):
                list_Veo_recente.append(i)
    return  list_Veo_recente
def observation(request):
    obs=request.GET.get('statutdoute')
    query=request.GET.get('observation')
    utilisateur=request.user.first_name +" "+ request.user.last_name
    email_traitement=request.user.username.title
    dos=request.GET.get('dos')
    Veoservices.objects.filter(id=dos).update(utilisateur=utilisateur)
    Veoservices.objects.filter(id=dos).update(email_traitement=email_traitement)
    NBD=nbrDAT()
    NBDT=nbrDT()
    ls=[]
    if (obs=="confirme"):
        Veoservices.objects.filter(id=dos).update(statutdoute="Doute confirmé")
    elif (obs=="rejete"):
        Veoservices.objects.filter(id=dos).update(statutdoute="Doute rejeté")
    elif (obs=="Attente"):
        Veoservices.objects.filter(id=dos).update(statutdoute="Attente photos Avant")
    elif (obs=="Pas sur"):
        Veoservices.objects.filter(id=dos).update(statutdoute="Pas sur")
    else:
        Veoservices.objects.filter(id=dos).update(statutdoute="Non traité")
    if query not in [None,""]:
        Veoservices.objects.filter(id=dos).update(observation=query)
        dateM=datetime.datetime.now()
        #ls=str(dateM).split('.')
       #dateM = ls[1]
        Veoservices.objects.filter(id=dos).update(date_obs=dateM)
    Veo=get_object_or_404(Veoservices,id=dos)
    Rate=Veo.RateFraude
    R1=round((Veo.Reg1()[0]*3/15),2)
    R1_P=Veo.Reg1()[1]
    R1_A=Veo.Reg1()[2]

    R2=round((Veo.Reg2()[0]*2)/15,2)
    R2_DDA=Veo.Reg2()[1]
    R2_DS=Veo.Reg2()[2]

    R3=round((Veo.Reg3()[0]*2)/15,2)
    R3_DDA=Veo.Reg3()[1]
    R3_DS=Veo.Reg3()[2]

    R4=round((Veo.Reg4()[0]*3)/15,2)
    R4_SP=Veo.Reg4()[1]
    R4_SA=Veo.Reg4()[2]

    R5=round((Veo.Reg5()[0]*2)/15,2)
    R5_Assis=Veo.Reg5()[1]

    R6=round((Veo.Reg6()[0]*2)/15,2)
    R6_Assis1=Veo.Reg6()[1]
    R6_Assis2=Veo.Reg6()[2]

    R7=Veo.Reg7()[0]
    R7_P=Veo.Reg7()[1]
    R7_A=Veo.Reg7()[2]

    R9=Veo.Reg9()[0]
    R9_DFP=Veo.Reg9()[1]
    R9_DS=Veo.Reg9()[2]


    R8=Veo.Reg8()

    R10=Veo.Reg10()[0]
    R10_Dos=Veo.Reg10()[1]
    
    R12=Veo.Reg12()[0]
    R12_Dos=Veo.Reg12()[1]

    R11=Veo.Reg11()

    R13=Veo.Reg13()[0]
    R13_Dos=Veo.Reg13()[1]

    R14=Veo.Reg14()

    context={"SupUse":SupUse(request),"NBDT":NBDT,"Veo":Veo,"Rate":Rate ,"R1": R1,"R1_P": R1_P, "R1_A":R1_A, "R2":R2, "R2_DDA":R2_DDA, "R2_DS":R2_DS,"R3":R3, "R3_DDA":R3_DDA, "R3_DS":R3_DS, "R4":R4, "R4_SP":R4_SP, "R4_SA":R4_SA,"R5":R5 ,"R5_Assis":R5_Assis ,"R6":R6,"R6_Assis1":R6_Assis1 ,"R6_Assis2":R6_Assis2,"R7":R7,"R7_P":R7_P,"R7_A":R7_A, "R9_DFP":R9_DFP, "R9_DS":R9_DS, "R9":R9,"R8":R8,"NBDossiers":NBD,"R11":R11, "R10_Dos":R10_Dos,"R10":R10 , "R12_Dos":R12_Dos,"R12":R12 , "R14":R14, "R13_Dos":R13_Dos,"R13":R13 }
    return render(request,"detail.html",context)


    
def filtre_reg(request):
    ch=request.GET.get('reg')
    
    liste=[]
    listedossiers =DosAff()
    if (ch=="R1"):
        for i in listedossiers:
            if i.R1 != None and i.R1 != "":
                liste.append(i)
    elif (ch =="R2"):
        for i in listedossiers:
            if i.R2 != None and i.R2 != "":
                liste.append(i)
    elif (ch =="R3"):
        for i in listedossiers:
            if i.R3 != None and i.R3 != "":
                liste.append(i)
        
    elif (ch =="R4"):
        for i in listedossiers:
            if i.R4 != None and i.R4 != "":
                liste.append(i)
    elif (ch =="R5"):
        for i in listedossiers:
            if i.R5 != None and i.R5 != "":
                liste.append(i)
    elif (ch =="R6"):
        for i in listedossiers:
            if i.R6 != None and i.R6 != "":
                liste.append(i)
    elif (ch =="R7"):
        for i in listedossiers:
            if i.R7 != None and i.R7 != "":
                liste.append(i)
    elif (ch =="R8"):
        for i in listedossiers:
            if i.R8 != None and i.R8 != "":
                liste.append(i)
    elif (ch =="R9"):
        for i in listedossiers:
            if i.R9 != None and i.R9 != "":
                liste.append(i)
    elif (ch =="R10"):
        for i in listedossiers:
            if i.R10 != None and i.R10 != "":
                liste.append(i)
    elif (ch =="R11"):
        for i in listedossiers:
            if i.R11 != None and i.R11 != "":
                liste.append(i)
    elif (ch =="R12"):
        for i in listedossiers:
            if i.R12 != None and i.R12 != "":
                liste.append(i)
    
    elif (ch =="R13_confirme"):
        for i in listedossiers:
            if i.R13 != None and "doute confirmé" in i.R13 :
                liste.append(i)

    elif (ch =="R13_rejete"):
        for i in listedossiers:
            if i.R13 != None and "doute rejeté" in i.R13 :
                liste.append(i)

                
    elif (ch =="R14"):
        for i in listedossiers:
            if i.R14 != None and i.R14 != "":
                liste.append(i)
    
    
    paginator = Paginator(liste,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    NBDAT=nbrDAT()    
    context={"SupUse":SupUse(request),"NBDossiers":NBDAT,"list_Veo_recente": veopg }
    return render(request,"home.html",context)





    
def filtre_regAT(request):
    ch=request.GET.get('reg')
    
    liste=[]
    listedossiers =DosAT()
    if (ch=="R1"):
        for i in listedossiers:
            if i.R1 != None and i.R1 != "":
                liste.append(i)
    elif (ch =="R2"):
        for i in listedossiers:
            if i.R2 != None and i.R2 != "":
                liste.append(i)
    elif (ch =="R3"):
        for i in listedossiers:
            if i.R3 != None and i.R3 != "":
                liste.append(i)
        
    elif (ch =="R4"):
        for i in listedossiers:
            if i.R4 != None and i.R4 != "":
                liste.append(i)
    elif (ch =="R5"):
        for i in listedossiers:
            if i.R5 != None and i.R5 != "":
                liste.append(i)
    elif (ch =="R6"):
        for i in listedossiers:
            if i.R6 != None and i.R6 != "":
                liste.append(i)
    elif (ch =="R7"):
        for i in listedossiers:
            if i.R7 != None and i.R7 != "":
                liste.append(i)
    elif (ch =="R8"):
        for i in listedossiers:
            if i.R8 != None and i.R8 != "":
                liste.append(i)
    elif (ch =="R9"):
        for i in listedossiers:
            if i.R9 != None and i.R9 != "":
                liste.append(i)
    elif (ch =="R10"):
        for i in listedossiers:
            if i.R10 != None and i.R10 != "":
                liste.append(i)
    elif (ch =="R11"):
        for i in listedossiers:
            if i.R11 != None and i.R11 != "":
                liste.append(i)
    elif (ch =="R12"):
        for i in listedossiers:
            if i.R12 != None and i.R12 != "":
                liste.append(i)
  
    elif (ch =="R13_confirme"):
        for i in listedossiers:
            if i.R13 != None and "doute confirmé" in i.R13 :
                liste.append(i)

    elif (ch =="R13_rejete"):
        for i in listedossiers:
            if i.R13 != None and "doute rejeté" in i.R13 :
                liste.append(i)

                
    elif (ch =="R14"):
        for i in listedossiers:
            if i.R14 != None and i.R14 != "":
                liste.append(i)

    paginator = Paginator(liste,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    NBD=nbrDAT()    
    
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"NBDossiers":NBD}
    
    return render(request,"dossieratrait.html",context)


    
def filtre_regT(request):
    ch=request.GET.get('reg')
    
    liste=[]
    listedossiers =DosTAff()
    if (ch=="R1"):
        for i in listedossiers:
            if i.R1 != None and i.R1 != "":
                liste.append(i)
    elif (ch =="R2"):
        for i in listedossiers:
            if i.R2 != None and i.R2 != "":
                liste.append(i)
    elif (ch =="R3"):
        for i in listedossiers:
            if i.R3 != None and i.R3 != "":
                liste.append(i)
        
    elif (ch =="R4"):
        for i in listedossiers:
            if i.R4 != None and i.R4 != "":
                liste.append(i)
    elif (ch =="R5"):
        for i in listedossiers:
            if i.R5 != None and i.R5 != "":
                liste.append(i)
    elif (ch =="R6"):
        for i in listedossiers:
            if i.R6 != None and i.R6 != "":
                liste.append(i)
    elif (ch =="R7"):
        for i in listedossiers:
            if i.R7 != None and i.R7 != "":
                liste.append(i)
    elif (ch =="R8"):
        for i in listedossiers:
            if i.R8 != None and i.R8 != "":
                liste.append(i)
    elif (ch =="R9"):
        for i in listedossiers:
            if i.R9 != None and i.R9 != "":
                liste.append(i)
    elif (ch =="R10"):
        for i in listedossiers:
            if i.R10 != None and i.R10 != "":
                liste.append(i)
    elif (ch =="R11"):
        for i in listedossiers:
            if i.R11 != None and i.R11 != "":
                liste.append(i)
    elif (ch =="R12"):
        for i in listedossiers:
            if i.R12 != None and i.R12 != "":
                liste.append(i)
  
    elif (ch =="R13_confirme"):
        for i in listedossiers:
            if i.R13 != None and "doute confirmé" in i.R13 :
                liste.append(i)

    elif (ch =="R13_rejete"):
        for i in listedossiers:
            if i.R13 != None and "doute rejeté" in i.R13 :
                liste.append(i)

                
    elif (ch =="R14"):
        for i in listedossiers:
            if i.R14 != None and i.R14 != "":
                liste.append(i)
    paginator = Paginator(liste,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    NBDAT=nbrDAT()    
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": DosAffdout(),"NBDossiers":NBDAT}
    
    return render(request,"dossiertrait.html",context)







##################################################################################################################
##################################################################################################################
##################################################################################################################
#################################################################################################################




####################################################################################################################*
#################################################################################################################*#*
#####################################################################################################################*
####################################################################################################################"
# *
# 
# 
# 
# 
# 
# 
# 
# 
# 

def test_nbrDAT():
    NBD=0
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo, '%d/%m/%Y %H:%M')
    list_veotest=veotest.objects.all()
    for i in list_veotest:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création, '%d/%m/%Y %H:%M')
            if (((Today_DateVeo-Date_création).days<=5) and i.statutdoute=="Non traité" and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) :
                NBD=NBD+1
    return NBD

def test_nbrDT():
    list_veotest=veotest.objects.all()
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo, '%d/%m/%Y %H:%M')
    NBD=0
    for i in list_veotest:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création, '%d/%m/%Y %H:%M')
            if ((Today_DateVeo-Date_création).days<=10 and (i.statutdoute=="Doute confirmé" or i.statutdoute=="Doute rejeté")   and i.Statut!="Dossier sans suite" and i.Statut!="Changement de procédure") :
                NBD=NBD+1
    return NBD


@login_required
def test_inis(request):
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo, '%d/%m/%Y %H:%M')
    NBDAT=test_nbrDAT()
    list_Veo_recente=[]
    NBD=0
    list_veotest=veotest.objects.all()
    Rate=0
    for i in list_veotest:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création, '%d/%m/%Y %H:%M')
            i.RateFraude = str_to_float(i.RateFraude)
        if (i.Statut!= "Changement procédure") and (i.RateFraude not in [0,0.0,None]):
            
            list_Veo_recente.append(i)
            
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"NBDossiers":NBDAT}
    return render(request,"home_test.html",context)

@login_required
def test_details(request, Dossier):
    Veo=get_object_or_404(veotest,id=Dossier)
    Rate=Veo.RateFraude
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    R1=Veo.Reg1()[0]
    R1_P=Veo.Reg1()[1]
    R1_A=Veo.Reg1()[2]

    R2=Veo.Reg2()[0]
    R2_DDA=Veo.Reg2()[1]
    R2_DS=Veo.Reg2()[2]

    R3=Veo.Reg3()[0]
    R3_DDA=Veo.Reg3()[1]
    R3_DS=Veo.Reg3()[2]

    R4=Veo.Reg4()[0]
    R4_SP=Veo.Reg4()[1]
    R4_SA=Veo.Reg4()[2]

    R5=Veo.Reg5()[0]
    #Dossier assistance qui à la  date moins  de 7h et plus de 20h
    R5_Assis=Veo.Reg5()[1]

    R6=Veo.Reg6()[0]
    #Les  deux dossiers Assistance qui ne dépassent pas 3 mois
    R6_Assis1=Veo.Reg6()[1]
    R6_Assis2=Veo.Reg6()[2]

    R7=Veo.Reg7()[0]
    R7_P=Veo.Reg7()[1]
    R7_A=Veo.Reg7()[2]

    R9=Veo.Reg9()[0]
    R9_DFP=Veo.Reg9()[1]
    R9_DS=Veo.Reg9()[2]

    R8=Veo.Reg8()

    R10=Veo.Reg10()[0]
    R10_Dos=Veo.Reg10()[1]
    
    R12=Veo.Reg12()[0]
    R12_Dos=Veo.Reg12()[1]

    R11=Veo.Reg11()

    R13=Veo.Reg13()[0]
    R13_Dos=Veo.Reg13()[1]

    R14=Veo.Reg14()
    # Vérifier si c'est superuser
    if request.user.is_superuser:
        SupUse = True
    else:
        SupUse = False
    context={"SupUse":SupUse, "NBDT":NBDT,"NBDossiers":NBD,"Veo":Veo,"Rate":Rate ,"R1": R1,"R1_P": R1_P, "R1_A":R1_A, "R2":R2, "R2_DDA":R2_DDA, "R2_DS":R2_DS,"R3":R3, "R3_DDA":R3_DDA, "R3_DS":R3_DS, "R4":R4, "R4_SP":R4_SP, "R4_SA":R4_SA,"R5":R5 ,"R5_Assis":R5_Assis ,"R6":R6,"R6_Assis1":R6_Assis1 ,"R6_Assis2":R6_Assis2,"R7":R7,"R7_P":R7_P,"R7_A":R7_A, "R9_DFP":R9_DFP, "R9_DS":R9_DS, "R9":R9,"R8":R8,"R11":R11, "R10_Dos":R10_Dos,"R10":R10 , "R12_Dos":R12_Dos,"R12":R12 ,"R14":R14, "R13_Dos":R13_Dos,"R13":R13 }

    return render(request,"detail_test.html",context)
def test_test_nbrDAT():
    NBD=0
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo, '%d/%m/%Y %H:%M')
    list_veotest=veotest.objects.all()
    for i in list_veotest:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création, '%d/%m/%Y %H:%M')
            if (((Today_DateVeo-Date_création).days<=5) and i.statutdoute=="Non traité" and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) :
                NBD=NBD+1
    return NBD

def test_nbrDT():
    list_veotest=veotest.objects.all()
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo, '%d/%m/%Y %H:%M')
    NBD=0
    for i in list_veotest:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création, '%d/%m/%Y %H:%M')
            if ((Today_DateVeo-Date_création).days<=10 and (i.statutdoute=="Doute confirmé" or i.statutdoute=="Doute rejeté")   and i.Statut!="Dossier sans suite" and i.Statut!="Changement de procédure") :
                NBD=NBD+1
    return NBD

def test_DosAff():
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo,'%d/%m/%Y %H:%M')
    list_Veo_recente=[]
    list_veotest=veotest.objects.all()

    for i in list_veotest:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création,'%d/%m/%Y %H:%M')
            if ((((Today_DateVeo-Date_création).days<=5) and (i.Statut!= "Changement procédure")) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" ) )and i.RateFraude not in [0,"0.0","","'0.0'",0.0,None]:
                list_Veo_recente.append(i)
    return  list_Veo_recente

def test_DosAT():
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo,'%d/%m/%Y %H:%M')
    list_Veo_recente=[]
    list_veotest=veotest.objects.all()

    for i in list_veotest:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création,'%d/%m/%Y %H:%M')
            if ((((Today_DateVeo-Date_création).days<=5) and (i.Statut!= "Changement procédure")) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" ) )and i.RateFraude not in [0,"0.0","","'0.0'",0.0,0,'0.0',None,'5.0','10.0']:
                list_Veo_recente.append(i)
    return  list_Veo_recente

def test_DosAffdout():
    list_Veo_recente =[]
    list_veotest = veotest.objects.all()
    NBD=test_nbrDAT()
    for i in list_veotest:
        if i.statutdoute == "Doute confirmé":
            list_Veo_recente.append(i)
    return  list_Veo_recente
def test_filtre(request):
    id=request.GET.get('filtre')
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    if (id=="Date_creation"):
        list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    elif (id=="Date_sinistre"):
        list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=True)
    else:
        for i in list_Veo_recente:
            i.RateFraude=str_to_float(i.RateFraude)
        list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
   # paginator = Paginator(list_Veo_recente,9)
   # page = request.GET.get('page')
   # veopg = paginator.get_page(page)
    #veopg.sort(key=lambda r: r.RateFraude,reverse=True)
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": list_Veo_recente}
    return render(request,"home_test.html",context)
    # Vérifier  si  l'utilisateur  connecter  est  un  admin
def test_SupUse(request):
    if request.user.is_superuser:
        SupUse = True
    else:
        SupUse = False
    return SupUse

def test_TrDos(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=1
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente":veopg ,"tri":tri}
    return render(request,"home_test.html",context)

def test_TrImmat(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=2
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrDsin(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=3
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrDcr(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=4
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrType(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=5
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrStat(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=6
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrExp(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=7
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrIAdv(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=8
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrRF(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=9
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrStatDoute(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=10
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_Trobs(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=11
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg , "tri":tri}
    return render(request,"home_test.html",context)


def test_TrDosI(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=12
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente":veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrImmatI(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=13
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrDsinI(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=14
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrDcrI(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=15
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrTypeI(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=16
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrStatI(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=17
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrExpI(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=18
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)

def test_TrIAdvI(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=19
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)
def test_TrRFI(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=20
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)
def test_TrStatDouteI(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=21
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)
def test_TrobsI(request):
    list_Veo_recente=test_DosAff()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=22
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)



def test_TrDosAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=1
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente":veopg ,"tri":tri}
    return render(request,"dossieratrait_test.html",context)

def test_TrImmatAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=2
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)
def test_TrDsinAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=3
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)
def test_TrDcrAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=4
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)

def test_TrTypeAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=5
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)
def test_TrStatAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=6
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)
def test_TrExpAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=7
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)

def test_TrIAdvAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=8
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)
def test_TrRFAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=9
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)
def test_TrStatDouteAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=10
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)
def test_TrobsAT(request):

    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=11
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg , "tri":tri}
    return render(request,"dossieratrait_test.html",context)


def test_TrDosIAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=12
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente":veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)

def test_TrImmatIAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=13
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)
def test_TrDsinIAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=14
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)

def test_TrDcrIAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=15
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)
def test_TrTypeIAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=16
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)
def test_TrStatIAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=17
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)
def test_TrExpIAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=18
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)

def test_TrIAdvIAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=19
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)
def test_TrRFIAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=20
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home_test.html",context)
def test_TrStatDouteIAT(request):
    
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=21
    context={"SupUse":SupUse(request),"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait_test.html",context)
def test_TrobsIAT(request):
    list_Veo_recente=test_DosAT()
    nbr=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=22
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri,"NBDT":NBDT}
    return render(request,"dossieratrait_test.html",context)


def test_TrDosT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=1
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)

def test_TrImmatT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=2
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrDsinT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=3
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrDcrT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=4
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)

def test_TrTypeT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=5
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)

def test_TrStatT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=6
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrExpT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=7
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)

def test_TrIAdvT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=8
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrRFT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=9
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)

def test_TrStatDouteT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=10
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrobsT(request):

    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=11
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)


def test_TrDosIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=12
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)

def test_TrImmatIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=13
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrDsinIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=14
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)

def test_TrDcrIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=15
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)

def test_TrDsinIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=14
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)

def test_TrDcrIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=15
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrTypeIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=16
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrStatIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=17
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrExpIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=18
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrIAdvIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=19
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrRFIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
        
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=20
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrStatDouteIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=21
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrobsIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=22
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)

def test_TrdateIT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r:  r.date_obs,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=24
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
def test_TrdateT(request):
    list_Veo_recente=test_DosTAff()
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r:  r.date_obs,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=23
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT, "tri":tri}
    return render(request,"dossiertrait_test.html",context)
@login_required
def test_filterDos(request):
    list_Veo_recente=[]
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo,'%d/%m/%Y %H:%M')
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    if request.method=='GET':
        query=request.GET.get('search')
    liste2=list(veotest.objects.filter(Dossier__icontains=query))
    liste1=list(veotest.objects.filter(Immatriculation__icontains=query))
    if liste1==None:
        liste=liste2
    elif liste2==None:
        liste=liste1
    else:
        liste=liste1+liste2
    for i in liste:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création,'%d/%m/%Y %H:%M')
            if ((Today_DateVeo-Date_création).days<=100) and i.RateFraude not in [0,'0.0',None,'5.0','10.0','15.0'] and i not in list_Veo_recente:
                list_Veo_recente.append(i)
                i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)

    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"NBDossiers":NBD,"NBDT":NBDT}
    return render(request,"home_test.html",context)
@login_required
def test_filterDosAT(request):
    list_Veo_recente=[]
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo,'%d/%m/%Y %H:%M')
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    if request.method=='GET':
        query=request.GET.get('search')
        liste2=list(veotest.objects.filter(Dossier__icontains=query))
        liste1=list(veotest.objects.filter(Immatriculation__icontains=query))
        if liste1==None:
            liste=liste2
        elif liste2==None:
            liste=liste1
        else:
            liste=liste1+liste2
        for i in liste:
            if i.Date_création!=None:
                Date_création=datetime.datetime.strptime(i.Date_création,'%d/%m/%Y %H:%M')
                if ((Today_DateVeo-Date_création).days<=100):
                    if (i.statutdoute=="Non traité" and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) and i not in list_Veo_recente:
                        list_Veo_recente.append(i)
                        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"NBDossiers":NBD,"NBDT":NBDT}
    return render(request,"dossieratrait_test.html",context)
@login_required
def test_filterDosT(request):
    list_Veo_recente=[]
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo,'%d/%m/%Y %H:%M')
    if request.method=='GET':
        query=request.GET.get('search')
        liste2=list(veotest.objects.filter(Dossier__icontains=query))
        liste1=list(veotest.objects.filter(Immatriculation__icontains=query))
        if liste1==None:
            liste=liste2
        elif liste2==None:
            liste=liste1
        else:
            liste=liste1+liste2
        for i in liste:
            if i.Date_création!=None:
                Date_création=datetime.datetime.strptime(i.Date_création,'%d/%m/%Y %H:%M')
                if ((Today_DateVeo-Date_création).days<=100):
                    if (i.statutdoute=="Doute confirmé" or i.statutdoute=="Doute rejeté") and i.Statut!="Changement de procédure" and  i.Statut!="Dossier sans suite" and i.RateFraude not in [0,'0.0',None,'5.0','10.0'] and i not in list_Veo_recente:
                        list_Veo_recente.append(i)
                        i.RateFraude=str_to_float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)

    
    Veoservice=veotest.objects.all()
    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT}
    return render(request,"dossiertrait_test.html",context)

@login_required
def test_dossierstrait(request):
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente=[]
    list_veotest=test_DosTAff()
    Veoservice=veotest.objects.all()
    for i in list_veotest:
        if (i.statutdoute=="Doute confirmé" or i.statutdoute=="Doute rejeté") and i.Statut!="Changement de procédure" and  i.Statut!="Dossier sans suite" :
            i.RateFraude = str_to_float(i.RateFraude)
            list_Veo_recente.append(i)

    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)

    list_Veo_Doute =[]
    for i in Veoservice:
        if i.statutdoute == "Doute confirmé":
            list_Veo_Doute.append(i)
    list_Veo_Doute.sort(key=lambda r: r.RateFraude,reverse=True)
    paginatorD = Paginator(list_Veo_Doute,9)
    pageD = request.GET.get('pageD')
    veoD = paginator.get_page(pageD)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBD,"NBDT":NBDT}
    return render(request,"dossiertrait_test.html",context)
@login_required
def test_dossiersAtrait(request):
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente=[]
    list_inst=[]
    list_veotest=test_DosAff()
    list_veotestall= veotest.objects.all()
    for i in list_veotestall:
        if i.Statut =="Dossier en instruction" and "D" in i.Dossier:
            list_inst.append(i)
    for i in list_veotest:
        
        if (i.statutdoute=="Non traité" and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) :
            i.RateFraude = str_to_float(i.RateFraude)
            list_Veo_recente.append(i)


    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
   # veopg.sort(key=lambda r: r.RateFraude,reverse=True)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"NBDossiers":NBD,"NBDT":NBDT ,"list_inst": list_inst}
    return render(request,"dossieratrait_test.html",context) 

def test_DosTAff():
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo,'%d/%m/%Y %H:%M')
    list_Veo_recente=[]
    list_veotest=veotest.objects.all()

    for i in list_veotest:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création,'%d/%m/%Y %H:%M')
            if ((Today_DateVeo-Date_création).days<=8) and (i.Statut!= "Changement procédure") and  (i.statutdoute=="Doute confirmé" or i.statutdoute=="Doute rejeté"):
                list_Veo_recente.append(i)
    return  list_Veo_recente
def test_observation(request):
    obs=request.GET.get('statutdoute')
    query=request.GET.get('observation')
    utilisateur=request.user.first_name +" "+ request.user.last_name
    email_traitement=request.user.username.title
    dos=request.GET.get('dos')
    veotest.objects.filter(id=dos).update(utilisateur=utilisateur)
    veotest.objects.filter(id=dos).update(email_traitement=email_traitement)
    NBD=test_nbrDAT()
    NBDT=nbrDT()
    ls=[]
    if (obs=="confirme"):
        veotest.objects.filter(id=dos).update(statutdoute="Doute confirmé")
    elif (obs=="rejete"):
        veotest.objects.filter(id=dos).update(statutdoute="Doute rejeté")
    elif (obs=="Attente"):
        veotest.objects.filter(id=dos).update(statutdoute="Attente photos Avant")
    elif (obs=="Pas sur"):
        veotest.objects.filter(id=dos).update(statutdoute="Pas sur")
    else:
        veotest.objects.filter(id=dos).update(statutdoute="Non traité")
    if query not in [None,""]:
        veotest.objects.filter(id=dos).update(observation=query)
        dateM=datetime.datetime.now()
        #ls=str(dateM).split('.')
       #dateM = ls[1]
        veotest.objects.filter(id=dos).update(date_obs=dateM)
    Veo=get_object_or_404(veotest,id=dos)
    Rate=Veo.RateFraude
    R1=round((Veo.Reg1()[0]*3/15),2)
    R1_P=Veo.Reg1()[1]
    R1_A=Veo.Reg1()[2]

    R2=round((Veo.Reg2()[0]*2)/15,2)
    R2_DDA=Veo.Reg2()[1]
    R2_DS=Veo.Reg2()[2]

    R3=round((Veo.Reg3()[0]*2)/15,2)
    R3_DDA=Veo.Reg3()[1]
    R3_DS=Veo.Reg3()[2]

    R4=round((Veo.Reg4()[0]*3)/15,2)
    R4_SP=Veo.Reg4()[1]
    R4_SA=Veo.Reg4()[2]

    R5=round((Veo.Reg5()[0]*2)/15,2)
    R5_Assis=Veo.Reg5()[1]

    R6=round((Veo.Reg6()[0]*2)/15,2)
    R6_Assis1=Veo.Reg6()[1]
    R6_Assis2=Veo.Reg6()[2]

    R7=Veo.Reg7()[0]
    R7_P=Veo.Reg7()[1]
    R7_A=Veo.Reg7()[2]

    R9=Veo.Reg9()[0]
    R9_DFP=Veo.Reg9()[1]
    R9_DS=Veo.Reg9()[2]


    R8=Veo.Reg8()

    R10=Veo.Reg10()[0]
    R10_Dos=Veo.Reg10()[1]
    
    R12=Veo.Reg12()[0]
    R12_Dos=Veo.Reg12()[1]

    R11=Veo.Reg11()

    R13=Veo.Reg13()[0]
    R13_Dos=Veo.Reg13()[1]

    R14=Veo.Reg14()

    context={"SupUse":SupUse(request),"NBDT":NBDT,"Veo":Veo,"Rate":Rate ,"R1": R1,"R1_P": R1_P, "R1_A":R1_A, "R2":R2, "R2_DDA":R2_DDA, "R2_DS":R2_DS,"R3":R3, "R3_DDA":R3_DDA, "R3_DS":R3_DS, "R4":R4, "R4_SP":R4_SP, "R4_SA":R4_SA,"R5":R5 ,"R5_Assis":R5_Assis ,"R6":R6,"R6_Assis1":R6_Assis1 ,"R6_Assis2":R6_Assis2,"R7":R7,"R7_P":R7_P,"R7_A":R7_A, "R9_DFP":R9_DFP, "R9_DS":R9_DS, "R9":R9,"R8":R8,"NBDossiers":NBD,"R11":R11, "R10_Dos":R10_Dos,"R10":R10 , "R12_Dos":R12_Dos,"R12":R12,"R14":R14, "R13_Dos":R13_Dos,"R13":R13 }
    return render(request,"detail_test.html",context)


def test_filtre_reg(request):
    ch=request.GET.get('reg')
    
    liste=[]
    listedossiers =test_DosAff()
    if (ch=="R1"):
        for i in listedossiers:
            if i.R1 != None and i.R1 != "":
                liste.append(i)
    elif (ch =="R2"):
        for i in listedossiers:
            if i.R2 != None and i.R2 != "":
                liste.append(i)
    elif (ch =="R3"):
        for i in listedossiers:
            if i.R3 != None and i.R3 != "":
                liste.append(i)
        
    elif (ch =="R4"):
        for i in listedossiers:
            if i.R4 != None and i.R4 != "":
                liste.append(i)
    elif (ch =="R5"):
        for i in listedossiers:
            if i.R5 != None and i.R5 != "":
                liste.append(i)
    elif (ch =="R6"):
        for i in listedossiers:
            if i.R6 != None and i.R6 != "":
                liste.append(i)
    elif (ch =="R7"):
        for i in listedossiers:
            if i.R7 != None and i.R7 != "":
                liste.append(i)
    elif (ch =="R8"):
        for i in listedossiers:
            if i.R8 != None and i.R8 != "":
                liste.append(i)
    elif (ch =="R9"):
        for i in listedossiers:
            if i.R9 != None and i.R9 != "":
                liste.append(i)
    elif (ch =="R10"):
        for i in listedossiers:
            if i.R10 != None and i.R10 != "":
                liste.append(i)
    elif (ch =="R11"):
        for i in listedossiers:
            if i.R11 != None and i.R11 != "":
                liste.append(i)
    elif (ch =="R12"):
        for i in listedossiers:
            if i.R12 != None and i.R12 != "":
                liste.append(i)
    
    elif (ch =="R13_confirme"):
        for i in listedossiers:
            if i.R13 != None and "doute confirmé" in i.R13 :
                liste.append(i)

    elif (ch =="R13_rejete"):
        for i in listedossiers:
            if i.R13 != None and "doute rejeté" in i.R13 :
                liste.append(i)

                
    elif (ch =="R14"):
        for i in listedossiers:
            if i.R14 != None and i.R14 != "":
                liste.append(i)
    paginator = Paginator(liste,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    NBDAT=test_nbrDAT()    
    context={"SupUse":SupUse(request),"NBDossiers":NBDAT,"list_Veo_recente": veopg }
    return render(request,"home_test.html",context)





    
def test_filtre_regAT(request):
    ch=request.GET.get('reg')
    
    liste=[]
    listedossiers =test_DosAT()
    if (ch=="R1"):
        for i in listedossiers:
            if i.R1 != None and i.R1 != "":
                liste.append(i)
    elif (ch =="R2"):
        for i in listedossiers:
            if i.R2 != None and i.R2 != "":
                liste.append(i)
    elif (ch =="R3"):
        for i in listedossiers:
            if i.R3 != None and i.R3 != "":
                liste.append(i)
        
    elif (ch =="R4"):
        for i in listedossiers:
            if i.R4 != None and i.R4 != "":
                liste.append(i)
    elif (ch =="R5"):
        for i in listedossiers:
            if i.R5 != None and i.R5 != "":
                liste.append(i)
    elif (ch =="R6"):
        for i in listedossiers:
            if i.R6 != None and i.R6 != "":
                liste.append(i)
    elif (ch =="R7"):
        for i in listedossiers:
            if i.R7 != None and i.R7 != "":
                liste.append(i)
    elif (ch =="R8"):
        for i in listedossiers:
            if i.R8 != None and i.R8 != "":
                liste.append(i)
    elif (ch =="R9"):
        for i in listedossiers:
            if i.R9 != None and i.R9 != "":
                liste.append(i)
    elif (ch =="R10"):
        for i in listedossiers:
            if i.R10 != None and i.R10 != "":
                liste.append(i)
    elif (ch =="R11"):
        for i in listedossiers:
            if i.R11 != None and i.R11 != "":
                liste.append(i)
    elif (ch =="R12"):
        for i in listedossiers:
            if i.R12 != None and i.R12 != "":
                liste.append(i)
  
    elif (ch =="R13_confirme"):
        for i in listedossiers:
            if i.R13 != None and "doute confirmé" in i.R13 :
                liste.append(i)

    elif (ch =="R13_rejete"):
        for i in listedossiers:
            if i.R13 != None and "doute rejeté" in i.R13 :
                liste.append(i)

                
    elif (ch =="R14"):
        for i in listedossiers:
            if i.R14 != None and i.R14 != "":
                liste.append(i)

    paginator = Paginator(liste,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    NBD=test_nbrDAT()    
    
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"NBDossiers":NBD}
    
    return render(request,"dossieratrait_test.html",context)


    
def test_filtre_regT(request):
    ch=request.GET.get('reg')
    
    liste=[]
    listedossiers =test_DosTAff()
    if (ch=="R1"):
        for i in listedossiers:
            if i.R1 != None and i.R1 != "":
                liste.append(i)
    elif (ch =="R2"):
        for i in listedossiers:
            if i.R2 != None and i.R2 != "":
                liste.append(i)
    elif (ch =="R3"):
        for i in listedossiers:
            if i.R3 != None and i.R3 != "":
                liste.append(i)
        
    elif (ch =="R4"):
        for i in listedossiers:
            if i.R4 != None and i.R4 != "":
                liste.append(i)
    elif (ch =="R5"):
        for i in listedossiers:
            if i.R5 != None and i.R5 != "":
                liste.append(i)
    elif (ch =="R6"):
        for i in listedossiers:
            if i.R6 != None and i.R6 != "":
                liste.append(i)
    elif (ch =="R7"):
        for i in listedossiers:
            if i.R7 != None and i.R7 != "":
                liste.append(i)
    elif (ch =="R8"):
        for i in listedossiers:
            if i.R8 != None and i.R8 != "":
                liste.append(i)
    elif (ch =="R9"):
        for i in listedossiers:
            if i.R9 != None and i.R9 != "":
                liste.append(i)
    elif (ch =="R10"):
        for i in listedossiers:
            if i.R10 != None and i.R10 != "":
                liste.append(i)
    elif (ch =="R11"):
        for i in listedossiers:
            if i.R11 != None and i.R11 != "":
                liste.append(i)
    elif (ch =="R12"):
        for i in listedossiers:
            if i.R12 != None and i.R12 != "":
                liste.append(i)
  
    elif (ch =="R13_confirme"):
        for i in listedossiers:
            if i.R13 != None and "doute confirmé" in i.R13 :
                liste.append(i)

    elif (ch =="R13_rejete"):
        for i in listedossiers:
            if i.R13 != None and "doute rejeté" in i.R13 :
                liste.append(i)

                
    elif (ch =="R14"):
        for i in listedossiers:
            if i.R14 != None and i.R14 != "":
                liste.append(i)

    paginator = Paginator(liste,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    NBDAT=test_nbrDAT()    
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"list_Veo_Doute": test_DosAffdout(),"NBDossiers":NBDAT}
    
    return render(request,"dossiertrait_test.html",context)

################## Affichage du  templates  ##############"##############"

def template(request):
    return render(request,"index.html")



def get_veoservices(request,Dossier):
    veoservice=Veoservices.objects.all()
    veo=None
    if request.method == 'GET':
        
       
        for i in  veoservice:
            if i.Dossier == Dossier:
                veo = i
                response = json.dumps([{'Dossier':Dossier,'Immatriculation':veo.Immatriculation,'Pourcentage Fraude':veo.RateFraude,'Procédure':veo.Procédure,'Statut':veo.Statut,'Date Création':veo.Date_création,'Statut doute':veo.statutdoute}])
                break
            if veo == None:

                response =  json.dumps([{'Error':Dossier}])
    response = json.loads(response)
    return HttpResponse(response, content_type='text/json')

"""def get_dossiers(request):
    veoservice=Veoservices.objects.all()
    ls=[]
    jsls=[]
    N=2
    for i in  veoservice:
        if i.RateFraude not in ["0.0",0.0,None,"0",0,"5.0",5.0,5,"10.0",10.0,10,"15.0",15.0,15]:
            ls.append(i)
    k=ls[0]
          
    l=ls[len(ls)-1]  
    jsls.append('[')  
    jsls.append({'Dossier':k.Dossier,'Pourcentage Fraude':k.RateFraude,'Procédure':k.Procédure,'Statut':k.Statut,'Date Création':k.Date_création,'Statut doute':k.statutdoute}) 
    for j  in  ls:
      
        if  j != k and j != l and N<1001:
            N=N+1
            jsls.append(",")
            js={'Dossier':j.Dossier,'Pourcentage Fraude':j.RateFraude,'Procédure':j.Procédure,'Statut':j.Statut,'Date Création':j.Date_création,'Statut doute':j.statutdoute}
            jsls.append(js)  
    jsls.append(",")  
    jsls.append({'Dossier':l.Dossier,'Pourcentage Fraude':l.RateFraude,'Procédure':l.Procédure,'Statut':l.Statut,'Date Création':l.Date_création,'Statut doute':l.statutdoute}) 
    jsls.append(']')
    #jsls = json.dumps(jsls)
    #jsls = json.loads(jsls)
    #jsl = [line for line in jsls]
    response = jsls
    return HttpResponse(response, content_type='text/json')"""
def  getVeos(request):
    veoservice=Veoservices.objects.all()
    #ls =[]
    
    #for i in  veoservice:
        
        #ls.append(i)
    ls = serialize('json', Veoservices.objects.all())
    response=ls
    
    return HttpResponse(response, content_type='text/json')


def get_dossiers(request):
    
    veoservice=Veoservices.objects.all()
    ls=[]
    jsls=[]
    N=2

    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo, '%d/%m/%Y %H:%M')
    NBD=0
    list_Veoservices=Veoservices.objects.all()
    Rate=0
    for i in list_Veoservices:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création, '%d/%m/%Y %H:%M')
            if ((Today_DateVeo-Date_création).days<=15) and i.RateFraude not in [0,'0.0',None]:
                ls.append(i)
    k=ls[0]
          
    l=ls[len(ls)-1]  
    jsls.append('[')  
    jsls.append({'Dossier':k.Dossier,'Pourcentage Fraude':k.RateFraude,'Procédure':k.Procédure,'Statut':k.Statut,'Date Création':k.Date_création,'Statut doute':k.statutdoute}) 
    for j  in  ls:
      
        if  j != k and j != l and N<1001:
            N=N+1
            jsls.append(",")
            js={'Dossier':j.Dossier,'Pourcentage Fraude':j.RateFraude,'Procédure':j.Procédure,'Statut':j.Statut,'Date Création':j.Date_création,'Statut doute':j.statutdoute}
            jsls.append(js)  
    jsls.append(",")  
    jsls.append({'Dossier':l.Dossier,'Pourcentage Fraude':l.RateFraude,'Procédure':l.Procédure,'Statut':l.Statut,'Date Création':l.Date_création,'Statut doute':l.statutdoute}) 
    jsls.append(']')
    #jsls = json.dumps(jsls)
    #jsls = json.loads(jsls)
    #jsl = [line for line in jsls]
    
    """if 'authorization' in request.headers and request.headers['authorization'] == 'Basic VeosmartAyODkwNUUteWx1LTIwTEM5RzRNQFZFT1NNQVJUV0FGQQ==':
        response = jsls
    else:
        response = json.dumps([{'Error':'Invalid Token'}])"""
    response = jsls
    return HttpResponse(response, content_type='text/json')
