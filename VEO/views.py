from django.shortcuts import render, get_object_or_404
from .models import Veodata, Assistance, Bris_De_Glace, Veoservices
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
import datetime
from django.core.paginator import Paginator





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

#@login_required
def Rate(request):
    list_veos=Veoservices.objects.all()
    context={"list_veos":list_veos}

    for i in list_veos:
        return render(request,"home.html",context)

def search(request):
    list=Veoservices.objects.all()
    listImm=[]
    sinisAd=[]
    for g in list:
        Preprocessing_Imm(g.Immatriculation)
        listImm.append(g.Immatriculation)

    if request.method=='GET':
        query=request.GET.get('search')
        Preprocessing_Imm(query)
        if query in listImm:
            list_veodata=Veodata.objects.filter(Immatriculation__icontains=query)
            list_veos=Veoservices.objects.filter(Immatriculation__icontains=query)
            list_Advr=Veoservices.objects.filter(ImmatriculationAdverse__icontains=query)
            list_Assis=Assistance.objects.filter(Immatriculation__icontains=query)
            list_BDG=Bris_De_Glace.objects.filter(Immatriculation__icontains=query)
            # #######################################################                 Partie Adverse            #################################################################""
            for i in list_Advr:
                i.strtodate()
                if sinisAd!=[]:
                        for j in sinisAd:
                            if  i.Dossier!=j.Dossier:
                                ok=True
                            else:
                                ok=False
                                break
                        if ok == True:
                            sinisAd.append(i)
                else:
                    sinisAd.append(i)
            #sort de la liste sinis selon la  date création
            sinisAd.sort(key=lambda r: r.CreatedDate ,reverse=True)
################################################################### Partie principale ################################################################################
            sinis=[]
            sous=[]
            List_P=[]
            for i in list_veodata:
                #convertion des types dates sinistre et création de str en date
                i.strtodate()
                # Pour ne pas répéter les lignes dans  l'affichage
                if i.Type!=None and  "Souscription" in i.Type:
                #convertion des types dates sinistre et création de str en date
                    List_P.append(i)
                #récupérer la  dernière souscription existante
                List_P.sort(key=lambda r: r.CreatedDate ,reverse=True)
                sous.append(List_P[0])
            for i in list_veos:
                if sinis!=[]:
                    for j in sinis:
                        if i.Dossier !=j.Dossier:
                            ok=True
                        else:
                            ok=False
                            break
                    if ok == True:
                        sinis.append(i)
                else:
                    sinis.append(i)
            Assis=[]
            for i in list_Assis:
                 #convertion des types dates sinistre et création de str en date
                i.strtodate()
                Assis.append(i)
            BDG=[]
            for i in list_BDG:
                #convertion des types dates sinistre et création de str en date
                i.strtodate()
                BDG.append(i)
            #sort de la liste sinis selon la  date création
            BDG.sort(key=lambda r: r.Datesinistre ,reverse=True)
            sinisAd.sort(key=lambda r: r.Date_sinistre ,reverse=True)
            Assis.sort(key=lambda r: r.DateAssistance ,reverse=True)
            sinis.sort(key=lambda r: r.Date_sinistre ,reverse=True)
      #      sum=0
     #       nbr=0
    #        for i in sinis:
            #    if  i.RateFraude!="" and i.RateFraude!=None:
           #         sum=sum+i.RateFraude
          #          nbr=nbr+1
         #   if nbr==0:
        #        nbr=1
       #     AVG= sum/nbr
            context={"sous": sous,"sinis": sinis, "sinisAd":sinisAd,"imm":query,"BDG":BDG,"Assis":Assis}
            return render(request,"search.html",context,)
        else:
            return HttpResponseRedirect('err/')


def err(request):
    return render(request,"err.html")

@login_required
def inis(request):
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo, '%d/%m/%Y %H:%M')
    NBDT=nbrDT()
    list_Veo_recente=[]
    NBD=0
    list_Veoservices=Veoservices.objects.all()
    Rate=0
    for i in list_Veoservices:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création, '%d/%m/%Y %H:%M')
        if ((Today_DateVeo-Date_création).days<=5) and (i.Statut!= "Changement procédure") and (i.RateFraude not in [0,'0.0',None]):
                #if (i.calcul!="oui"):
       #         if i.Reg1()!=None:
        #            R1=i.Reg1()[0]
         #       else:
          #                R1=0
     #           if i.Reg2()!=None:
      #              R2=i.Reg2()[0]
       #         else:
        #            R2=0
         #       if i.Reg3()!=None:
          #          R3=i.Reg3()[0]
           #     else:
            #        R3=0
    #            if i.Reg4()!=None:
     #               R4=i.Reg4()[0]
      #          else:
       #             R4=0
        #        if i.Reg5()!=None:
         #           R5=i.Reg5()[0]
          #      else:
           #         R5=0
  #              if i.Reg6()!=None:
   #                 R6=i.Reg6()[0]
    #            else:
     #               R6=0
      #          if i.Reg7()!=None:
       #             R7=i.Reg7()[0]
        #        else:
         #           R7=0
          #      if i.Reg9()!=None:
           #         R9=i.Reg9()[0]
            #    else:
             #       R9=0
              #  if i.Reg8()!=None:
    #                R8=i.Reg8()
     #           else:
      #              R8=0

       #         Rate=R1+R2+R3+R4+R5+R6+R7+R9+R8
        #        Veoservices.objects.filter(Dossier=i.Dossier).update(calcul="oui")
         #       if Rate<=100:
          #          Veoservices.objects.filter(Dossier=i.Dossier).update(RateFraude=round(Rate,2))
           #         Veoservices.objects.filter(Dossier=i.Dossier).update(statutdoute="Non traité")
            #    else:
             #       Rate=100
              #      Veoservices.objects.filter(Dossier=i.Dossier).update(RateFraude=Rate)
               #     Veoservices.objects.filter(Dossier=i.Dossier).update(statutdoute="Non traité")
            
              #  i.RateFraude=float(i.RateFraude)
                list_Veo_recente.append(i)
                if ( i.Statut!="Changement de procédure" and i.RateFraude not in [0,"0.0",None,"5.0","10.0"] and i.statutdoute =="Non traité" ) or  (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']):
                    NBD=NBD+1
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
   # veopg.sort(key=lambda r: r.RateFraude,reverse=True)

    context={"SupUse":SupUse(request),"NBDT":NBDT,"list_Veo_recente": veopg,"NBDossiers":NBD}
    return render(request,"home.html",context)

@login_required
def details(request, Dossier):

    Veo=get_object_or_404(Veoservices,id=Dossier)
    Rate=Veo.RateFraude
    NBD=nbrDAT()
    NBDT=nbrDT()
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
    #Dossier assistance qui à la  date moins  de 7h et plus de 20h
    R5_Assis=Veo.Reg5()[1]

    R6=round((Veo.Reg6()[0]*2)/15,2)
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
    # Vérifier si c'est superuser
    if request.user.is_superuser:
        SupUse = True
    else:
        SupUse = False

    context={"SupUse":SupUse, "NBDT":NBDT,"NBDossiers":NBD,"Veo":Veo,"Rate":Rate ,"R1": R1,"R1_P": R1_P, "R1_A":R1_A, "R2":R2, "R2_DDA":R2_DDA, "R2_DS":R2_DS,"R3":R3, "R3_DDA":R3_DDA, "R3_DS":R3_DS, "R4":R4, "R4_SP":R4_SP, "R4_SA":R4_SA,"R5":R5 ,"R5_Assis":R5_Assis ,"R6":R6,"R6_Assis1":R6_Assis1 ,"R6_Assis2":R6_Assis2,"R7":R7,"R7_P":R7_P,"R7_A":R7_A, "R9_DFP":R9_DFP, "R9_DS":R9_DS, "R9":R9,"R8":R8}

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
            if ((Today_DateVeo-Date_création).days<=5 and (i.statutdoute=="Doute confirmé" or i.statutdoute=="Doute rejeté")   and i.Statut!="Dossier sans suite" and i.Statut!="Changement de procédure") :
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
            if (((Today_DateVeo-Date_création).days<=5) and (i.Statut!= "Changement procédure")) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" ):
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
            i.RateFraude=float(i.RateFraude)
        list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
   # paginator = Paginator(list_Veo_recente,9)
   # page = request.GET.get('page')
   # veopg = paginator.get_page(page)
    #veopg.sort(key=lambda r: r.RateFraude,reverse=True)
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": list_Veo_recente}
    return render(request,"home.html",context)
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
        i.RateFraude=float(i.RateFraude)
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
        i.RateFraude=float(i.RateFraude)
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=9
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossieratrait.html",context)
def TrStatDouteAT(request):
    list_Veo_recente=DosAff()
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

    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=20
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"home.html",context)
def TrStatDouteIAT(request):
    
    list_Veo_recente=DosAff()
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
    list_Veo_recente=DosAff()
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
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=1
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente":veopg ,"tri":tri}
    return render(request,"dossiertrait.html",context)

def TrImmatT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=2
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrDsinT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=3
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrDcrT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=4
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrTypeT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=5
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrStatT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=6
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrExpT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=7
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrIAdvT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=8
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrRFT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=9
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrStatDouteT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=10
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrobsT(request):

    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=11
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg , "tri":tri}
    return render(request,"dossiertrait.html",context)


def TrDosIT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.id,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=12
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente":veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrImmatIT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Immatriculation,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=13
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrDsinIT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=14
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrDcrIT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=15
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrDsinIT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=14
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)

def TrDcrIT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=15
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrTypeIT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Procédure,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=16
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrStatIT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Statut,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=17
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrExpIT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.Expert,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=18
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrIAdvIT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.ImmatriculationAdverse,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=19
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrRFIT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    for i in list_Veo_recente:
        i.RateFraude=float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
        
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=20
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrStatDouteIT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.statutdoute,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=21
    context={"SupUse":SupUse(request),"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri}
    return render(request,"dossiertrait.html",context)
def TrobsIT(request):
    list_Veo_recente=DosTAff()
    nbr=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente.sort(key=lambda r: r.observation,reverse=False)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    tri=22
    context={"SupUse":SupUse(request),"NBDT":NBDT,"NBDossiers":nbr,"list_Veo_recente": veopg, "tri":tri,"NBDT":NBDT}
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
            if ((Today_DateVeo-Date_création).days<=2) and i.RateFraude not in [0,'0.0',None,'5.0','10.0','15.0'] and i not in list_Veo_recente:
                list_Veo_recente.append(i)
                i.RateFraude=float(i.RateFraude)
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
                if ((Today_DateVeo-Date_création).days<=2):
                    if (i.statutdoute=="Non traité" and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) and i not in list_Veo_recente:
                        list_Veo_recente.append(i)
                        i.RateFraude=float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"NBDossiDrs":NBD,"NBDT":NBDT}
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
                if ((Today_DateVeo-Date_création).days<=0):
                    if (i.statutdoute=="Doute confirmé" or i.statutdoute=="Doute rejeté") and i.Statut!="Changement de procédure" and  i.Statut!="Dossier sans suite" and i.RateFraude not in [0,'0.0',None,'5.0','10.0'] and i not in list_Veo_recente:
                        list_Veo_recente.append(i)
                        i.RateFraude=float(i.RateFraude)
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)

    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"NBDossiers":NBD,"NBDT":NBDT}
    return render(request,"dossiertrait.html",context)
@login_required
def DosFrauduleux(request):
     list_Veoservices=Veoservices.objects.filter(RateFraude!=0).filter(RateFraude!='0.0').filter(RateFraude!=None)
     return list_Veoservices
@login_required
def dossierstrait(request):
    NBD=nbrDAT()
    NBDT=nbrDT()
    list_Veo_recente=[]
    list_Veoservices=DosAff()
    Veoservice=Veoservices.objects.all()
    for i in list_Veoservices:
        if (i.statutdoute=="Doute confirmé" or i.statutdoute=="Doute rejeté") and i.Statut!="Changement de procédure" and  i.Statut!="Dossier sans suite" :
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
    list_Veoservices=DosAff()
    for i in list_Veoservices:
        if (i.statutdoute=="Non traité" and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) or (i.statutdoute=="Attente photos Avant" and i.Photos_Avant!="" and i.Photos_Avant!=None and i.Statut!="Changement de procédure" and i.RateFraude not in [0,'0.0',None,'5.0','10.0']) :
            i.RateFraude = float(i.RateFraude)
            list_Veo_recente.append(i)


    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    paginator = Paginator(list_Veo_recente,9)
    page = request.GET.get('page')
    veopg = paginator.get_page(page)
   # veopg.sort(key=lambda r: r.RateFraude,reverse=True)
    context={"SupUse":SupUse(request),"list_Veo_recente": veopg,"NBDossiers":NBD,"NBDT":NBDT}
    return render(request,"dossieratrait.html",context) 

def DosTAff():
    Today_DateVeo=datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo,'%d/%m/%Y %H:%M')
    list_Veo_recente=[]
    list_Veoservices=Veoservices.objects.all()

    for i in list_Veoservices:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création,'%d/%m/%Y %H:%M')
            if ((Today_DateVeo-Date_création).days<=5) and (i.Statut!= "Changement procédure") and  (i.statutdoute=="Doute confirmé" or i.statutdoute=="Doute rejeté"):
                list_Veo_recente.append(i)
    return  list_Veo_recente
def observation(request):
    obs=request.GET.get('statutdoute')
    query=request.GET.get('observation')
    dos=request.GET.get('dos')
    NBD=nbrDAT()
    NBDT=nbrDT()
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

    context={"SupUse":SupUse(request),"NBDT":NBDT,"Veo":Veo,"Rate":Rate ,"R1": R1,"R1_P": R1_P, "R1_A":R1_A, "R2":R2, "R2_DDA":R2_DDA, "R2_DS":R2_DS,"R3":R3, "R3_DDA":R3_DDA, "R3_DS":R3_DS, "R4":R4, "R4_SP":R4_SP, "R4_SA":R4_SA,"R5":R5 ,"R5_Assis":R5_Assis ,"R6":R6,"R6_Assis1":R6_Assis1 ,"R6_Assis2":R6_Assis2,"R7":R7,"R7_P":R7_P,"R7_A":R7_A, "R9_DFP":R9_DFP, "R9_DS":R9_DS, "R9":R9,"R8":R8,"NBDossiers":NBD}
    return render(request,"detail.html",context)


    















