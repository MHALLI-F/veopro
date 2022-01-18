from django.db import models
from datetime import datetime


# Create your models here.
def inter_dt(dtV , dtE):  
    if (dtV and dtE):  
        dtV = datetime.strptime(dtV, "%d/%m/%Y").date()
        dtE = datetime.strptime(dtE, "%d/%m/%Y").date()
        return abs(dtV - dtE).days 
def inter_dt2(dtV,dtE):  
    if (dtV and dtE):  
        dtV= datetime.strptime(dtV, "%d/%m/%Y").date()
        dtE = datetime.strptime(dtE, "%d/%m/%Y").date()
        return (dtE- dtV).days 

############################################################### Nettoyage des immatriculations
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


class Veodata(models.Model):
    id = models.TextField(primary_key=True)
    Type=models.TextField()
    ContactName=models.TextField()
    Immatriculation=models.TextField()
    ImmatriculationAdverse=models.TextField()
    Okpoursouscription=models.TextField()
    Statutgarage=models.TextField()
    record_id=models.TextField()
    CreatedDate=models.TextField()
    Datesinistre=models.TextField()
    Nomintermédiairecp=models.TextField()
    def strtodate(self):
        if self.CreatedDate!=None and self.CreatedDate!="":
            self.CreatedDate=datetime.strptime(self.CreatedDate, "%Y-%m-%d %H:%M:%S")
        if self.Datesinistre!="" and self.Datesinistre!=None:
            
            self.Datesinistre=datetime.strptime(self.Datesinistre, "%Y-%m-%d")
        return self

class Assistance(models.Model):
    id = models.TextField(primary_key=True)
    Type=models.TextField()
    Prestataire=models.TextField()

    Statut=models.TextField()
#    RéférenceVeo=models.TextField()
    Intervention=models.TextField()
    Immatriculation=models.TextField()
    Nomclient=models.TextField()
    PhotosRemorquage=models.TextField()
    PhotosConstat=models.TextField()
    DateRemorquage=models.TextField()
    DateConstat=models.TextField()
    Ref_knk=models.TextField()   
    
    def strtodate(self):
        if self.DateAssistance!=None:
            self.DateAssistance=datetime.strptime(self.DateAssistance, "%d/%m/%Y")
        return self

class Bris_De_Glace(models.Model):
    id = models.AutoField(primary_key=True)
    Type=models.TextField()
    Référencedossier=models.TextField()
    Immatriculation=models.TextField()
    Datesinistre=models.TextField()
    NomAssuré_souscripteur=models.TextField()
    PhotosAvant=models.TextField()
    PhotosAprès=models.TextField()
    Statut=models.TextField()
    Datedecréation=models.TextField()


    def strtodate(self):
        if self.Datedecréation!=None and self.Datesinistre!=None:
            self.Datedecréation=datetime.strptime(self.Datedecréation, "%d/%m/%Y %H:%M")
            self.Datesinistre=datetime.strptime(self.Datesinistre, "%d/%m/%Y")
        return self

   
class Veoservices(models.Model):
    id = models.TextField(primary_key=True)
    Ref_knk=models.TextField()
    Dossier=models.TextField()
    Statut=models.TextField()
    Date_sinistre=models.TextField()
    Garantie=models.TextField()
    Procédure=models.TextField()
    Expert=models.TextField()
    Immatriculation=models.TextField()
    Date_création=models.TextField()
    Date_validité_début=models.TextField()
    Date_validité_fin=models.TextField()	
    Date_validité_début_Adv=models.TextField()	
    Date_validité_fin_Adv=models.TextField()	
    RateFraude=models.FloatField()
    Photos_Avant=models.TextField()	
    Photos_en_cours=models.TextField()	
    Photos_après_réparation=models.TextField()
    ImmatriculationAdverse=models.TextField()
    calcul=models.TextField()
    R1=models.TextField()
    R2=models.TextField()
    R3=models.TextField()
    R4=models.TextField()
    R5=models.TextField()
    R6=models.TextField()
    R7=models.TextField()
    R8=models.TextField()
    R9=models.TextField()
    date_obs=models.DateTimeField()
    observation=models.TextField()
    statutdoute=models.TextField()

    def strtodate(self):
        if self.Date_création!=None and self.Date_sinistre!=None and self.Date_validité_début_Adv!=None and self.Date_validité_fin_Adv!=None and self.Date_validité_fin!=None and self.Date_validité_début!=None:        
            self.Date_création=datetime.strptime(self.Date_création, "%Y-%m-%d %H:%M:%S")
            self.Date_sinistre=datetime.strptime(self.Date_sinistre, "%Y-%m-%d %H:%M:%S")
            self.Date_validité_début=datetime.strptime(self.Date_validité_début, "%Y-%m-%d %H:%M:%S")
            self.Date_validité_fin=datetime.strptime(self.Date_validité_fin, "%Y-%m-%d %H:%M:%S")
            self.Date_validité_début_Adv=datetime.strptime(self.Date_validité_début_Adv, "%Y-%m-%d %H:%M:%S")
            self.Date_validité_fin_Adv=datetime.strptime(self.Date_validité_fin_Adv, "%Y-%m-%d %H:%M:%S")     
        return self


    def Reg1(self):
        R=None
        
        
        Rate=0
        Imm_princ=Preprocessing_Imm(self.Immatriculation)
        Imm_Adv=Preprocessing_Imm(self.ImmatriculationAdverse)
        Liste=list(Veodata.objects.all())

        for j in Liste:
                
            if Imm_princ not in [None,""] and (Preprocessing_Imm(j.Immatriculation) == Imm_princ or Preprocessing_Imm(j.ImmatriculationAdverse) == Imm_princ) and ((j.Statutgarage is not  None) and (j.Statutgarage.lower()=="cas douteux")):
                Rate=30
                R="30%: l'immatriculation principale a déjà été impliquée dans un dossier historique signalé douteux "+str(j.id)
                #La declaration douteux pour  afficher le  détail
                doute_Princ=j
                break
            else:
                doute_Princ=None
        for i in Liste:
            if Imm_Adv not in [None,""] and (Preprocessing_Imm(i.Immatriculation) == Imm_Adv or Preprocessing_Imm(i.ImmatriculationAdverse) == Imm_Adv) and ((i.Statutgarage is not  None) and (i.Statutgarage.lower()=="cas douteux")):
                Rate=30
                R="30%: l'immatriculation adverse a déjà été impliquée dans un dossier historique signalé douteux: "+str(i.id)
                #La declaration douteux pour  afficher le  détail
                doute_Adv=i
                break 
            else:
                doute_Adv=None
        Veoservices.objects.filter(id=self.id).update(R1=R)       
        return [Rate,doute_Princ,doute_Adv]




    def Reg2(self):
        R=None
        self.Immatriculation=Preprocessing_Imm(self.Immatriculation)
        self.ImmatriculationAdverse=Preprocessing_Imm(self.ImmatriculationAdverse)
        Rate=0
        #self.strtodate()
        DDP=self.Date_validité_début
        date_sinis=self.Date_sinistre
        if date_sinis!=None or date_sinis!="":
            if DDP!=None:
                diff_sous_sinis=inter_dt2(date_sinis, DDP)
                if diff_sous_sinis!=None  and  0<=diff_sous_sinis<=30:
                    Rate=10  
                    R="10%: Ce sinistre survenu moins d'un mois après date début d'assurance: "+self.Date_validité_début
                elif diff_sous_sinis!=None  and diff_sous_sinis==0:
                    Rate=20
                    R="20%: Ce sinistre survenu dans le même jour de la début d'assurance: "+self.Date_validité_début
                else:
                    DDP=None
                    date_sinis=None
        Veoservices.objects.filter(id=self.id).update(R2=R)   
        return [Rate,DDP,date_sinis]

      

    def  Reg3(self):
        R=None
        self.Immatriculation=Preprocessing_Imm(self.Immatriculation)
        self.ImmatriculationAdverse=Preprocessing_Imm(self.ImmatriculationAdverse)
        Rate=0      
        #self.strtodate()
        DDA=self.Date_validité_début_Adv
        date_sinis=self.Date_sinistre
        if date_sinis!=None or date_sinis!="":
            if DDA!=None:
                diff_sous_sinis=inter_dt2(date_sinis, DDA)
                if diff_sous_sinis!=None  and 0<=diff_sous_sinis<=30:
                    Rate=10  
                    R="10%: sinistre survenu moins d'un mois après date début d'assurance de la partie adverse: "+self.Date_validité_début_Adv
                elif diff_sous_sinis!=None  and diff_sous_sinis==0:
                    Rate=20
                    R="20%: Ce sinistre survenu dans le même jour de la début d'assurance: "+self.Date_validité_début
                else:
                    DDA=None
                    date_sinis=None      
        else:
            DDA=None
            date_sinis=None     
        Veoservices.objects.filter(id=self.id).update(R3=R)   
        return [Rate,DDA,date_sinis]
        
        

    def Reg4(self):
        Rate=0
        R=None
        Imm_Adv=Preprocessing_Imm(self.ImmatriculationAdverse)
        Imm_princ=Preprocessing_Imm(self.Immatriculation)
        Liste=list(Veodata.objects.filter( Type__icontains="Souscription"))
        for A in Liste:
            if Imm_princ not in [None,""] and Preprocessing_Imm(A.Immatriculation) == Imm_princ and A.Okpoursouscription=="NOK":
                Rate=15
                R="15%: l'immatriculation adverse a été signalée comme souscription NOK voir le dossier "+str(A.id)
                A=A
                break
            else:
                Rate=0
                A=None
        for A in  Liste:
            if Imm_Adv not in [None,""] and Preprocessing_Imm(A.Immatriculation) == Imm_Adv and A.Okpoursouscription=="NOK":
                Rate=15
                R="15%: l'immatriculation principale a été signalée comme souscription NOK voir le dossier "+str(i.id)
                P=A
                break
            else:
                Rate=0
                P=None
        Veoservices.objects.filter(id=self.id).update(R4=R)   
        return  [Rate,P,A]
        
        


    def  Reg5(self):
        Rate=0
        A=None
        R=None
        Liste2=[]
        Liste=[]
        Date_création=datetime.strptime(self.Date_sinistre, "%d/%m/%Y")
        Imm_princ=Preprocessing_Imm(self.Immatriculation)
        Liste=list(Assistance.objects.all())
        for i in Liste:
            if (Imm_princ not in [None,""] and Preprocessing_Imm(i.Immatriculation) == Imm_princ) and (i.DateConstat != None or i.DateRemorquage != None) and (i.PhotosConstat !=None or i.PhotosRemorquage != None):
                Liste2.append(i)
        if Liste2!=[]:
            for i in Liste2:
                if i.Intervention == "Remorquage" and i.DateRemorquage != None and i.DateRemorquage != '':
                    DateAssistance=datetime.strptime(i.DateRemorquage, "%d/%m/%Y %H:%M")
                    if  0<=((DateAssistance-Date_création).days)<=5:
                        if DateAssistance.hour<7  or DateAssistance.hour>=20:
                            Rate=10
                            R="10%: La date assistance du dossier: "+str(i.id)+" est après 20h ou avant 7h du matin"
                            A=i
                            break
                elif i.DateConstat != None and i.DateConstat != '':
                    DateAssistance=datetime.strptime(i.DateConstat, "%d/%m/%Y %H:%M")
                    if  0<=((DateAssistance-Date_création).days)<=5:
                        if DateAssistance.hour<7  or DateAssistance.hour>=20:
                            Rate=10
                            R="10%: La date assistance du dossier: "+str(i.id)+" est après 20h ou avant 7h du matin"
                            A=i
                            break
        Veoservices.objects.filter(id=self.id).update(R5=R)                       
        return [Rate,A]

    def  Reg6(self):
        Rate=0 
        R=None  
        A1=None
        A2=None 
        liste2=[]
        Imm_princ=Preprocessing_Imm(self.Immatriculation)
        Imm_Adv=Preprocessing_Imm(self.ImmatriculationAdverse)     
        Liste=list(Assistance.objects.all())
        DateAssistance1 = None
        DateAssistance2 = None
        for i in Liste:
            if (Imm_princ not in [None,""] and Preprocessing_Imm(i.Immatriculation) == Imm_princ) and (i.DateConstat != None or i.DateRemorquage != None) and (i.PhotosConstat !=None or i.PhotosRemorquage != None):
                liste2.append(i)
        for i in  liste2:
            if i.Intervention == "Remorquage" and i.DateRemorquage != None and i.DateRemorquage != '':
                DateAssistance1=datetime.strptime(i.DateRemorquage, "%d/%m/%Y %H:%M")
            elif i.DateConstat != None and i.DateConstat != '':
                    DateAssistance1=datetime.strptime(i.DateConstat, "%d/%m/%Y %H:%M")
           # else:
            #DateAssistance1=None
            for j in liste2:
                if i!=j:
                    if j.Intervention == "Remorquage" and j.DateRemorquage != None and j.DateRemorquage != '':
                                
                        DateAssistance2=datetime.strptime(j.DateRemorquage, "%d/%m/%Y %H:%M")
                        if DateAssistance1 != None and DateAssistance2 != None:
                            if 1<abs((DateAssistance2-DateAssistance1).days)<=90:
                                Rate=5
                                R="5%: les 2 dossiers "+str(j.id)+" et "+str(i.id)+" ont moins de 3 mois de distance"
                                A1=j
                                A2=i
                                break

                    elif j.DateConstat != None and j.DateConstat != '':
                        DateAssistance2=datetime.strptime(j.DateConstat, "%d/%m/%Y %H:%M")
                        if DateAssistance1 != None and DateAssistance2 !=None : 
                            if 1<abs((DateAssistance2-DateAssistance1).days)<=90:
                                Rate=5
                                R="5%: les 2 dossiers "+str(j.id)+" et "+str(i.id)+" ont moins de 3 mois de distance"
                                A1=j
                                A2=i
                                break
        Veoservices.objects.filter(id=self.id).update(R6=R)                   
        return [Rate,A1,A2]


    def Reg7(self):
        if ((self.Procédure is not None) and ("Souscription" not in self.Procédure)):
            Rate=0
            R=None
            A=None
            P=None
            liste2=[]
            liste1=[]
           
            Liste=list(Veoservices.objects.all())
            Imm_princ=Preprocessing_Imm(self.Immatriculation)
            for i in Liste:
                if i.Date_sinistre != self.Date_sinistre and (Imm_princ not in [None,""] and Preprocessing_Imm(i.Immatriculation) == Imm_princ):
                        liste2.append(i)
            date_sinis1=self.Date_sinistre
            for j in liste2:
                date_sinis2=j.Date_sinistre
                if (date_sinis2!=None and date_sinis2!="")and (date_sinis1!=None and date_sinis1!=""):                   
                    diff=inter_dt(date_sinis1, date_sinis2)
                    if ((diff!=None) and (1<diff<=365)) and  j.Statut != "Changement de procédure":
                        
                        Rate=5
                        R="5%: l'immatriculation principale a déjà fait l'objet d'un sinistre il y'a moins de 12 mois " +str(j.id)
                        P=j
                        break
                        


            Imm_adv=Preprocessing_Imm(self.ImmatriculationAdverse)        
            for i in Liste:
                
                if i.Date_sinistre != self.Date_sinistre and (Imm_princ not in [None,""] and Preprocessing_Imm(i.Immatriculation) == Imm_princ):
                    liste1.append(i)
            date_sinis1=self.Date_sinistre
            for j in liste1:
                date_sinis2=j.Date_sinistre
                if (date_sinis2!=None and date_sinis2!="")and (date_sinis1!=None and date_sinis1!=""):                   
                    diff=inter_dt(date_sinis1, date_sinis2)
                    if ((diff!=None) and (1<diff<=365)) and j.Statut != "Changement de procédure":
                        Rate=5
                        A=j
                        R="5%: l'immatriculation adverse a déjà fait l'objet d'un sinistre il y'a moins de 12 mois "+str(j.id)
                            
                        
                        break
                        
        Veoservices.objects.filter(id=self.id).update(R7=R)                   
        return  [Rate,P,A]
        
        
    def  Reg9(self):
        R=None
        
        Rate=0
        #self.strtodate()
        DFP=self.Date_validité_fin
        date_sinis=self.Date_sinistre
        if self.Garantie != None:
            if (date_sinis!=None) and (date_sinis!="") and ("tierce" in self.Garantie.lower()):
                if DFP!=None:
                    diff_sous_sinis=inter_dt2(date_sinis,DFP)
                    if diff_sous_sinis!=None  and 0<diff_sous_sinis<=30:
                        Rate=5  
                        R="5%: La  garantie  est Tierce  et il reste moins  d'un mois avant la fin  de  validité  de  contrat: "+self.Date_validité_fin
                else:
                    DFP=None
                    date_sinis=None
        Veoservices.objects.filter(id=self.id).update(R9=R)   
        return [Rate,DFP,date_sinis]
        
    def  Reg8(self):
        R=None
        self.Immatriculation=Preprocessing_Imm(self.Immatriculation)
        self.ImmatriculationAdverse=Preprocessing_Imm(self.ImmatriculationAdverse)
        Rate=0
        #self.strtodate()
        
        if (self.ImmatriculationAdverse!=None) and (self.ImmatriculationAdverse!="") and (len(self.ImmatriculationAdverse)>=12):
            
            Rate=10 
            R="10%: La  partie  adverse est un cyclo: "+self.ImmatriculationAdverse
                
        Veoservices.objects.filter(id=self.id).update(R8=R)   
        return Rate






    
