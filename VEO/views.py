from django.shortcuts import render, get_object_or_404
from .models import Veodata, Assistance, Bris_De_Glace, Veoservices
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
import datetime






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

                            if  i.Date_création!=j.Date_création or i.Date_sinistre!=j.Date_sinistre or i.Immatriculation!=j.Immatriculation or  i.ImmatriculationAdverse!=j.ImmatriculationAdverse or  i.Statut!=j.Statut:
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

                        if i.Date_création!=j.Date_création or i.Date_sinistre!=j.Date_sinistre or i.Immatriculation!=j.Immatriculation or  i.ImmatriculationAdverse!=j.ImmatriculationAdverse or  i.Statut!=j.Statut:
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
                
                #if Assis!=[]:
                    #for j in Assis:

                        #if i.ContactName!=j.ContactName or i.CreatedDate!=j.CreatedDate or i.Datesinistre!=j.Datesinistre or i.Immatriculation!=j.Immatriculation or i.NomIntermédiaire!=j.NomIntermédiaire or i.ImmatriculationAdverse!=j.ImmatriculationAdverse or  i.StatutDétaillé!=j.StatutDétaillé :
                            #ok=True
                            
                        #else:
                            #ok=False
                            #break

                    #if ok == True: 
                        #Assis.append(i)
                #else:
                    
                    #Assis.append(i)
                             
            BDG=[]
            for i in list_BDG:
                #convertion des types dates sinistre et création de str en date
                i.strtodate()
                BDG.append(i)
                
                #if BDG!=[]:
                    #for j in BDG:

                        #if i.Atelier!=j.Atelier or i.CreatedDate!=j.CreatedDate or i.Datesinistre!=j.Datesinistre or i.Immatriculation!=j.Immatriculation or i.NomIntermédiaire!=j.NomIntermédiaire or i.ImmatriculationAdverse!=j.ImmatriculationAdverse or  i.StatutDétaillé!=j.StatutDétaillé :
                            #ok=True
                            
                        #else:
                            #ok=False
                            #break

                    #if ok == True: 
                        #BDG.append(i)
                #else:
                    
                    #BDG.append(i)
                                     
                                
                       
            #sort de la liste sinis selon la  date création         
            
            BDG.sort(key=lambda r: r.Datesinistre ,reverse=True)
            sinisAd.sort(key=lambda r: r.Date_sinistre ,reverse=True)
            Assis.sort(key=lambda r: r.DateAssistance ,reverse=True)     
            sinis.sort(key=lambda r: r.Date_sinistre ,reverse=True)    
            sum=0  
            nbr=0 

            for i in sinis:
                if  i.RateFraude!="" and i.RateFraude!=None:
                    sum=sum+i.RateFraude
                    nbr=nbr+1

            if nbr==0:
                nbr=1    
            AVG= sum/nbr
            

           



            context={"sous": sous,"sinis": sinis, "sinisAd":sinisAd,"imm":query,"BDG":BDG,"Assis":Assis, "AVG":AVG}

            
            
            return render(request,"search.html",context,)
 
        else:
            return HttpResponseRedirect('err/')
        
    
def err(request):
    
    return render(request,"err.html")

@login_required
def inis(request):
    Today_DateVeo=datetime.datetime.today().strftime('%d %b, %Y %H:%M:%S')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo, '%d %b, %Y %H:%M:%S')
    Today_DateAss=datetime.datetime.today().strftime("%m/%d/%Y")
    Today_DateAss=datetime.datetime.strptime(Today_DateAss, "%m/%d/%Y")
    Today_DateBDG=datetime.datetime.today().strftime("%m/%d/%Y %H:%M")
    Today_DateBDG=datetime.datetime.strptime(Today_DateBDG, "%m/%d/%Y %H:%M")
    list_Veo_recente=[]
    list_Veoservices=Veoservices.objects.all()
    Rate=0
    for i in list_Veoservices:
        if i.Date_création!=None:
            Date_création=datetime.datetime.strptime(i.Date_création, '%d %b, %Y %H:%M:%S')
            if ((Today_DateVeo-Date_création).days<=1) and (i.Statut!= "Changement procédure"):
                if i.Reg1()!=None:
                    R1=i.Reg1()[0] 
                else: 
                    R1=0
                if i.Reg2()!=None:
                    R2=i.Reg2()[0]
                else: 
                   R2=0 
                if i.Reg3()!=None:
                    R3=i.Reg3()[0] 
                else: 
                    R3=0    
                if i.Reg5()!=None:
                    R4=i.Reg4()[0]
                else: 
                    R4=0 
                if i.Reg5()!=None:
                   R5=i.Reg5()[0]
                else: 
                    R5=0
                if i.Reg6()!=None:
                    R6=i.Reg6()[0]
                else:
                    R6=0
                if i.Reg7()!=None:
                    R7=i.Reg7()[0] 
                else: 
                    R7=0
                if i.Reg9()!=None:
                    R9=i.Reg9()[0] 
                else: 
                    R9=0
                if i.Reg8()!=None:
                    R8=i.Reg8() 
                else: 
                    R8=0
                
                Rate=R1+R2+R3+R4+R5+R6+R7+R9+R8
               
            if Rate<=100:
                Veoservices.objects.filter(Dossier=i.Dossier).update(RateFraude=round(Rate,2))   
                Veoservices.objects.filter(Dossier=i.Dossier).update(observation="Pas sur")
            else:
                Rate=100
                Veoservices.objects.filter(Dossier=i.Dossier).update(RateFraude=Rate)
                Veoservices.objects.filter(Dossier=i.Dossier).update(observation="Pas sur")    
        if ((i.RateFraude!=0) and (i.RateFraude!=None) and (i.RateFraude!="0.0")):
            list_Veo_recente.append(i)
        #list_Veoservices.sort(key=lambda r: r.RateFraude,reverse=True) 
        #list_Veo_recente=[list_Veodata[0],list_Veodata[1],list_Veodata[2],list_Veodata[3],list_Veodata[4]]
        #list_Assistance.sort(key=lambda r: r.RateFraude,reverse=True)
        #list_Assistance_recente=[list_Assistance[0],list_Assistance[1],list_Assistance[2],list_Assistance[3],list_Assistance[4]]
        #list_BDG.sort(key=lambda r: r.RateFraude,reverse=True)
        #list_BDG_recente=[list_BDG[0],list_BDG[1],list_BDG[2],list_BDG[3],list_BDG[4]]
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    context={"list_Veo_recente": list_Veo_recente}
    return render(request,"home.html",context)

           
           
        




def details(request, id):
    Veo=get_object_or_404(Veoservices,id=id)
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
     
    context={"Veo":Veo,"Rate":Rate ,"R1": R1,"R1_P": R1_P, "R1_A":R1_A, "R2":R2, "R2_DDA":R2_DDA, "R2_DS":R2_DS,"R3":R3, "R3_DDA":R3_DDA, "R3_DS":R3_DS, "R4":R4, "R4_SP":R4_SP, "R4_SA":R4_SA,"R5":R5 ,"R5_Assis":R5_Assis ,"R6":R6,"R6_Assis1":R6_Assis1 ,"R6_Assis2":R6_Assis2,"R7":R7,"R7_P":R7_P,"R7_A":R7_A, "R9_DFP":R9_DFP, "R9_DS":R9_DS, "R9":R9,"R8":R8}

    return render(request,"detail.html",context)
    
def filtre(request):
    id=request.GET.get('filtre')
    Today_DateVeo=datetime.datetime.today().strftime('%d %b, %Y %H:%M:%S')
    Today_DateVeo=datetime.datetime.strptime(Today_DateVeo, '%d %b, %Y %H:%M:%S')
    list_Veo_recente=[]
    list_Veoservices=Veoservices.objects.all()
   
    for i in list_Veoservices:
        if i.Date_création!=None:  
            Date_création=datetime.datetime.strptime(i.Date_création, '%d %b, %Y %H:%M:%S')
            if ((Today_DateVeo-Date_création).days<=100) and (i.Statut!= "Changement procédure"):
                if ((i.RateFraude!=0) and (i.RateFraude!=None)):
                    list_Veo_recente.append(i)
    if (id=="Date_creation"):
        list_Veo_recente.sort(key=lambda r: r.Date_création,reverse=True)
    elif (id=="Date_sinistre"):
        list_Veo_recente.sort(key=lambda r: r.Date_sinistre,reverse=True)   
    else:
        list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True) 
    context={"list_Veo_recente": list_Veo_recente}
    return render(request,"home.html",context)
def observation(request):
    obs=request.GET.get('observation')
    dos=request.GET.get('dos')
    if (obs=="confirme"):
        Veoservices.objects.filter(id=dos).update(observation="Doute confirmé")
    elif (obs=="rejete"):
        Veoservices.objects.filter(id=dos).update(observation="Doute rejeté")   
    else:
        Veoservices.objects.filter(id=dos).update(observation="Pas sur") 
        
    list_Veo_recente=[]
    list_Veoservices=Veoservices.objects.all()
    
    for i in list_Veoservices:
        if (i.RateFraude!=0) and (i.RateFraude!=None) and (i.RateFraude!= 0.0):
            list_Veo_recente.append(i)
        
    list_Veo_recente.sort(key=lambda r: r.RateFraude,reverse=True)
    context={"list_Veo_recente": list_Veo_recente}
    return render(request,"home.html",context)





