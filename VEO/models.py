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
        dtV= datetime.satrptime(dtV, "%d/%m/%Y").date()
        dtE = datetime.strptime(dtE, "%d %b, %Y %H:%M:%S").date()
        return (dtE- dtV).days 

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


class Veodata(models.Model):
    id = models.AutoField(primary_key=True)
    CaseNumber=models.TextField()
    Type=models.TextField()
    ContactName=models.TextField()
    Immatriculation=models.TextField()
    ImmatriculationAdverse=models.TextField()
    NumérodePolice=models.TextField()
    NumérodePoliceAdverse=models.TextField()
    TypeAppréciation=models.TextField()
    ClientOKavecchiffrage=models.TextField()
    Okpoursouscription=models.TextField()
    Statutgarage=models.TextField()
    AssignedTo=models.TextField()
    Indemnité_calculauto=models.TextField()
    Status=models.TextField()
    CreatedDate=models.TextField()
    ResolutionActual=models.TextField()
    Datesinistre=models.TextField()
    DatePEC=models.TextField()
    Daterdv=models.TextField()
    CodeIntermédiaire=models.TextField()
    VilleIntervention=models.TextField()
    Nomintermédiairecp=models.TextField()
    Garages=models.TextField()
    Devisgarage=models.TextField()
    Observationssurledossierfaitsmarquants=models.TextField()
    Idd=models.TextField()
    Statutdetaillé=models.TextField()
    Instanceàtraiter=models.TextField()
    DatePhotosAvantWP=models.TextField()
    EmailWP=models.TextField()
    def strtodate(self):
        if self.CreatedDate!=None and self.Datesinistre!=None and self.DatePEC!=None and self.Daterdv!=None and self.DatePhotosAvantWP!=None:        
            self.CreatedDate=datetime.strptime(self.CreatedDate, "%d %b, %Y %H:%M:%S")
            self.Datesinistre=datetime.strptime(self.Datesinistre, "%d %b, %Y %H:%M:%S")
            self.DatePEC=datetime.strptime(self.DatePEC, "%d %b, %Y %H:%M:%S")
            self.Daterdv=datetime.strptime(self.Daterdv, "%d %b, %Y %H:%M:%S")
            self.DatePhotosAvantWP=datetime.strptime(self.DatePhotosAvantWP, "%d %b, %Y %H:%M:%S")
        return self

class Assistance(models.Model):
    id = models.AutoField(primary_key=True)
    Type=models.TextField()
    Idd=models.TextField()
    Prestataire=models.TextField()
    DateAssistance=models.TextField()
    Statut=models.TextField()
    RéférenceVeo=models.TextField()
    Intervention=models.TextField()
    Immatriculation=models.TextField()
    NumérodePolice=models.TextField()
    Nomclient=models.TextField()
    PhotosAvant=models.TextField()
    PhotosAprès=models.TextField()
    PhotosConstat=models.TextField()
    PhotosHistorique=models.TextField()
    DatePhotosAvant=models.TextField()
    DatePhotosaprès=models.TextField()
    Datedépartremorquage=models.TextField()
    DatePhotosConstat=models.TextField()
    DateAssistance_h=models.TextField()
   
    
    def strtodate(self):
        if self.DateAssistance!=None and self.DatePhotosAvant!=None and self.DatePhotosaprès!=None and self.Datedépartremorquage !=None and self.DatePhotosConstat!=None:
            self.DateAssistance=datetime.strptime(self.DateAssistance, "%d/%m/%Y")
            self.DatePhotosAvant=datetime.strptime(self.DatePhotosAvant, "%d %b, %Y %H:%M:%S")
            self.DatePhotosaprès=datetime.strptime(self.DatePhotosaprès, "%d %b, %Y %H:%M:%S")
            self.Datedépartremorquage=datetime.strptime(self.Datedépartremorquage,"%d %b, %Y %H:%M:%S")
            self.DatePhotosConstat=datetime.strptime(self.DatePhotosConstat, "%d %b, %Y %H:%M:%S")
        return self

class Bris_De_Glace(models.Model):
    id = models.AutoField(primary_key=True)
    Type=models.TextField()
    Idd=models.TextField()
    Référencedossier=models.TextField()
    Compagnie=models.TextField()
    Immatriculation=models.TextField()
    Datesinistre=models.TextField()
    NumérodePolice=models.TextField()
    Numérodesinistre=models.TextField()
    NomAssuré_souscripteur=models.TextField()
    PhotosAvant=models.TextField()
    PhotosAprès=models.TextField()
    Réseau=models.TextField()
    Statut=models.TextField()
    Datedecréation=models.TextField()
    Datedefacturation=models.TextField()
    Délaidefacturation_h=models.TextField()
    Cat_facturation=models.TextField()
    Dateenvoiedevis=models.TextField()
    Dateenvoieaccord=models.TextField()
    DélaidetraitementdesDevis_h=models.TextField()
    Cat_traitementDevis=models.TextField()
    Atelier=models.TextField()
    Nombredeglacesendommagées=models.TextField()
    Ducompagnie_Dhs=models.TextField()
    Duassuré_Dhs=models.TextField()
    Dateclôturedossier=models.TextField()
    

    def strtodate(self):
        if self.Dateclôturedossier!=None and self.Dateenvoiedevis!=None and self.Dateenvoieaccord!=None and self.Datedefacturation!=None and self.Datedecréation!=None and self.Datesinistre!=None:
            self.Dateclôturedossier=datetime.strptime(self.Dateclôturedossier, "%d/%m/%Y %H:%M")
            self.Dateenvoiedevis=datetime.strptime(self.Dateenvoiedevis, "%d/%m/%Y %H:%M")
            self.Dateenvoieaccord=datetime.strptime(self.Dateenvoieaccord, "%d/%m/%Y %H:%M")
            self.Datedefacturation=datetime.strptime(self.Datedefacturation, "%d/%m/%Y %H:%M")
            self.Datedecréation=datetime.strptime(self.Datedecréation, "%d/%m/%Y %H:%M")
            self.Datesinistre=datetime.strptime(self.Datesinistre, "%d/%m/%Y")
        return self

   
class Veoservices(models.Model):
    id = models.AutoField(primary_key=True)
    Idd=models.TextField()
    Dossier=models.TextField()
    Statut=models.TextField()
    Statut_gestion=models.TextField()
    Date_sinistre=models.TextField()
    Marque=models.TextField()
    Modèle=models.TextField()
    Date_de_mise_en_circulation=models.TextField()
    Garantie=models.TextField()
    Code_intermédiaire=models.TextField()
    Octroi_VHR=models.TextField()
    Cat_VHR=models.TextField()
    Durée_VHR=models.TextField()
    Durée_réparation=models.TextField()
    Code_Garage=models.TextField()
    Code_Expert=models.TextField()
    Code_Procédure=models.TextField()
    Montant_initial_accord=models.TextField()
    Montant_modifié_accord=models.TextField()
    Etat_dossier=models.TextField()
    Procédure=models.TextField()
    Expert=models.TextField()
    Garage=models.TextField()
    Immatriculation=models.TextField()
    Dû_compagnie_GA=models.TextField()
    Dû_compagnie_RC=models.TextField()
    Devis_peinture_TTC=models.TextField()
    Devis_Pièces_TTC=models.TextField()
    Devis_garage_TTC=models.TextField()
    Accord_Dommages_TTC=models.TextField()
    Rapport_Peinture_TTC=models.TextField()
    Rapport_Pièces_TTC =models.TextField()
    Montant_Dommages_rapport_TTC=models.TextField()
    TVA_à_déduire=models.TextField()
    Vétusté_appliquée=models.TextField()
    Franchise_appliquée=models.TextField()
    Dû_compagnie=models.TextField()
    Dû_assuré=models.TextField()
    Date_création=models.TextField()
    Date_envoi_devis_garage=models.TextField()
    Date_Accord_Expert=models.TextField()
    Date_règlement=models.TextField()
    Date_accord_compagnie=models.TextField()
    Date_envoi_demande_2e_accord=models.TextField()
    Date_prédéclaration=models.TextField()
    Date_validation_rapport_contrôle=models.TextField()
    Date_rejet_accord_compagnie=models.TextField()
    Login_accord_compagnie=models.TextField()
    Date_état_des_lieux=models.TextField()
    Date_Photos_Avant=models.TextField()
    Date_Photos_après=models.TextField()
    Date_Photos_en_cours=models.TextField()
    Date_2ème_accord=models.TextField()
    Date_envoi_facture=models.TextField()
    Date_FFT=models.TextField()
    Date_publication_rapport=models.TextField()
    Date_validation_mission=models.TextField()
    Date_CDC=models.TextField()
    Début_VHR=models.TextField()
    Fin_VHR=models.TextField()
    Date_retour_véhicule=models.TextField()
    Rdv_client=models.TextField()
    Rdv_initial_client=models.TextField()
    Facture_Peinture_TTC=models.TextField()
    Facture_Pièces_TTC=models.TextField()
    Facture_Garage_TTC=models.TextField()
    Différence_montant_accord=models.TextField()
    Motif_rejet_rapport=models.TextField()
    Date_FFT_signée=models.TextField()
    Date_de_mise_en_instance_PEC_Mission=models.TextField()
    Date_de_mise_en_instance_règlement=models.TextField()
    Dommage_Collision=models.TextField()
    RC=models.TextField()
    Durée_VHR_Calculée=models.TextField()
    Nature_Rdv=models.TextField()
    Mise_en_instance_PEC_Mission=models.TextField()
    Mise_en_instance_règlement=models.TextField()
    Montant_Dommages_1_accord_TTC=models.TextField()
    Motif_de_changement_de_procédure=models.TextField()
    Type_Garage=models.TextField()
    Date_rejet_rapport=models.TextField()
    Num_déclaration=models.TextField()
    Date_validité_début=models.TextField()
    Date_validité_fin=models.TextField()	
    Date_validité_début_Adv=models.TextField()	
    Date_validité_fin_Adv=models.TextField()	
    Dossier_douteux=models.TextField()
    RateFraude=models.FloatField()
    Photos_Avant=models.TextField()	
    Photos_en_cours=models.TextField()	
    Photos_après_réparation=models.TextField()
    ImmatriculationAdverse=models.TextField()
    R1=models.TextField()
    R2=models.TextField()
    R3=models.TextField()
    R4=models.TextField()
    R5=models.TextField()
    R6=models.TextField()
    R7=models.TextField()
    R8=models.TextField()
    R9=models.TextField()
    observation=models.TextField()

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
        if Imm_princ== None:
            List_Princ=[]
        else:
            List_Princ1=list(Veodata.objects.filter(Immatriculation=Imm_princ).exclude( Type__icontains="Souscription"))
            List_Princ2=list(Veodata.objects.filter(ImmatriculationAdverse=Imm_princ))
            if (((List_Princ1==[]) ) and (List_Princ2==[])):
                List_Princ=[]
            if (((List_Princ1==[])) and (List_Princ2!=[])):
                List_Princ=List_Princ2
            if (((List_Princ2==[])) and (List_Princ1!=[])):
                List_Princ=List_Princ1
            if ((List_Princ1!=[])and (List_Princ2!=[])):
                List_Princ=List_Princ1 + List_Princ2   
        if Imm_Adv==None:
            List_Adv=[]
        else:
            List_Adv1=list(Veodata.objects.filter(Immatriculation=Imm_Adv).exclude( Type__icontains="Souscription"))
            List_Adv2=list(Veodata.objects.filter(ImmatriculationAdverse=Imm_Adv))
            if ((List_Adv1==[]) and (List_Adv2 == [])):
                List_Adv=[]
            if ((List_Adv1==[]) and (List_Adv2!=[])):
                List_Adv=List_Adv2
            if ((List_Adv1!=[]) and (List_Adv2==[])):
                List_Adv=List_Adv1
            if ((List_Adv1!=[]) and (List_Adv2!=[])):
                List_Adv=List_Adv1 + List_Adv2

        if  (List_Princ!=[]):
            for j in List_Princ:
                if ((j.Statutgarage is not  None) and (j.Statutgarage.lower()=="cas douteux")):
                    Rate=30
                    R="30%: l'immatriculation principale a déjà été impliquée dans un dossier historique signalé douteux "+str(j.CaseNumber)
                    #La declaration douteux pour  afficher le  détail
                    doute_Princ=j
                    break
                else:
                    doute_Princ=None
        else:
            doute_Princ=None
        if (List_Adv!=[]):
            for i in List_Adv:
                if ((i.Statutgarage is not  None) and (i.Statutgarage.lower()=="cas douteux")):
                    Rate=30
                    R="30%: l'immatriculation adverse a déjà été impliquée dans un dossier historique signalé douteux: "+str(i.CaseNumber)
                    #La declaration douteux pour  afficher le  détail
                    doute_Adv=i
                    break 
                else:
                    doute_Adv=None
        else:
            doute_Adv=None
        Veoservices.objects.filter(Dossier=self.Dossier).update(R1=R)       
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
                if 0<=diff_sous_sinis<=30:
                    Rate=10  
                    R="10%: Ce sinistre survenu moins d'un mois après date début d'assurance: "+self.Date_validité_début
                else:
                    DDP=None
                    date_sinis=None
        Veoservices.objects.filter(Dossier=self.Dossier).update(R2=R)   
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
                if 0<=diff_sous_sinis<=30:
                    Rate=10  
                    R="10%: sinistre survenu moins d'un mois après date début d'assurance de la partie adverse: "+self.Date_validité_début_Adv
                else:
                    DDA=None
                    date_sinis=None      
        else:
            DDA=None
            date_sinis=None     
        Veoservices.objects.filter(Dossier=self.Dossier).update(R3=R)   
        return [Rate,DDA,date_sinis]
        
        

    def Reg4(self):
        Rate=0
        R=None
        
        
        Imm_Adv=Preprocessing_Imm(self.ImmatriculationAdverse)
        Imm_princ=Preprocessing_Imm(self.Immatriculation)
        if self.ImmatriculationAdverse!=None:
            
            List_A=list(Veodata.objects.filter(Immatriculation=Imm_Adv ).filter( Type__icontains="Souscription"))
            
            for i in List_A:
                i.strtodate()
            List_A.sort(key=lambda r: r.CreatedDate ,reverse=True)
        else:       
            List_A=[]
        if Imm_princ== None:
            
            List_P=[]
        else:
            
            List_P=list(Veodata.objects.filter(Immatriculation=Imm_princ ).filter(Type__icontains="Souscription"))
            for i in List_P:
                i.strtodate()
            List_P.sort(key=lambda r: r.CreatedDate ,reverse=True)

        if List_A!=[]:
            A=List_A[0]
            for A in  List_A:
                if i.Okpoursouscription=="NOK":
                    Rate=15
                    R="15%: l'immatriculation adverse a été signalée comme souscription NOK voir le dossier "+str(i.CaseNumber)
                    A=List_A[0]
                    break
                else:
                    Rate=0
                    A=None
        else:
            A=None
        if List_P!=[]:
            P=List_P[0]
            for A in  List_A:
                if i.Okpoursouscription=="NOK":
                    Rate=15
                    R="15%: l'immatriculation principale a été signalée comme souscription NOK voir le dossier "+str(i.CaseNumber)
                    P=List_P[0]
                    break
                else:
                    Rate=0
                    P=None
        else:
            P=None
        Veoservices.objects.filter(Dossier=self.Dossier).update(R4=R)   
        return  [Rate,P,A]
        
        


    def  Reg5(self):
        Rate=0    
        A=None
        R=None
          
        Date_création=datetime.strptime(self.Date_sinistre, "%d/%m/%Y")
        Imm_princ=Preprocessing_Imm(self.Immatriculation)
        if Imm_princ!=None:
            List_Princ=list(Assistance.objects.filter(Immatriculation=Imm_princ).exclude( PhotosHistorique="").exclude(PhotosHistorique=None))
        else:
            List_Princ=[]
        if List_Princ!=[]:
            for i in List_Princ:
                
                DateAssistance=datetime.strptime(i.DateAssistance, "%d/%m/%Y")
                if 0<=((DateAssistance-Date_création).days)<=5 and i.DateAssistance_h!=None:
                    date=datetime.strptime(i.DateAssistance_h, "%d %b, %Y %H:%M:%S")
                    if date.hour<=7  or date.hour>=20:
                        Rate=10
                        R="10%: La date assistance du dossier: "+str(i.RéférenceVeo)+" est après 20h ou avant 7h du matin"
                        A=i
                        break
                        
                
        Veoservices.objects.filter(Dossier=self.Dossier).update(R5=R)                       
        return [Rate,A]

    def  Reg6(self):
        Rate=0 
        R=None  
        A1=None
        A2=None 
        
            
        Imm_princ=Preprocessing_Imm(self.Immatriculation)
        Imm_Adv=Preprocessing_Imm(self.ImmatriculationAdverse)     
        if Imm_princ!=None:
            List_Princ1=list(Assistance.objects.filter(Immatriculation=Imm_princ).exclude( PhotosHistorique="").exclude(PhotosHistorique=None))
        else:
            List_Princ1=[]
        if Imm_Adv!=None:
            List_Princ2=list(Assistance.objects.filter(Immatriculation=Imm_Adv).exclude( PhotosHistorique="").exclude(PhotosHistorique=None))
        else:
            List_Princ2=[]
        List_Princ=List_Princ1+List_Princ2
        if List_Princ!=[]:
            for i in List_Princ:
                
                DateAssistance1=datetime.strptime(i.DateAssistance, "%d/%m/%Y")
                for j in List_Princ:
                    if i!=j:
                        DateAssistance2=datetime.strptime(j.DateAssistance, "%d/%m/%Y")
                        if 0<abs((DateAssistance2-DateAssistance1).days)<=90:
                            
                                
                            Rate=5
                            R="5%: les 2 dossiers "+str(i.RéférenceVeo)+" et "+str(j.RéférenceVeo)+" ont moins de 3 mois de distance"
                            A1=j
                            A2=i
                            break
                            # j'ai multiplier par  2  par  ce  que  il  doit  avoir  deux  
                            # dossier  pour  comparer  donc  à chaque  fois  qu'il sera détécter  la  liste  contient 2  dossiers 
        Veoservices.objects.filter(Dossier=self.Dossier).update(R6=R)                   
        return [Rate,A1,A2]


    def Reg7(self):
        if ((self.Procédure is not None) and ("Souscription" not in self.Procédure)):
            Rate=0
            R=None
            A=None
            P=None
            
           

            Imm_princ=Preprocessing_Imm(self.Immatriculation)
            if Imm_princ is None:
                List_Princ=[]
                List_P=[]
            else:
                if self.Date_sinistre!=None:
                    List_P=Veoservices.objects.filter(Immatriculation=Imm_princ).exclude( Procédure__icontains="Souscription").exclude(Date_sinistre__icontains=self.Date_sinistre)
                    date_sinis1=self.Date_sinistre
                else:
                    List_P=Veoservices.objects.filter(Immatriculation=Imm_princ).exclude( Procédure__icontains="Souscription")
                date_sinis1=self.Date_sinistre
                for j in List_P:
                    date_sinis2=j.Date_sinistre
                    if (date_sinis2!=None and date_sinis2!="")and (date_sinis1!=None and date_sinis1!=""):                   
                        diff=inter_dt(date_sinis1, date_sinis2)
                        if ((diff!=None) and (0<diff<=365)):
                            Rate=5
                            R="5%: l'immatriculation principale a déjà fait l'objet d'un sinistre il y'a moins de 12 mois " +str(j.Dossier)
                            P=j
                            break
                        


            Imm_adv=Preprocessing_Imm(self.ImmatriculationAdverse)        
            if Imm_adv is None:  
                List_A=[]
            else:
                if self.Date_sinistre!=None:
                    List_A=Veoservices.objects.filter(Immatriculation=Imm_adv ).exclude( Procédure__icontains="Souscription").exclude(Date_sinistre__icontains=self.Date_sinistre)
                    
                else:
                    List_A=Veoservices.objects.filter(Immatriculation=Imm_adv ).exclude( Procédure__icontains="Souscription")  
                date_sinis1=self.Date_sinistre
                for j in List_A:
                    date_sinis2=j.Date_sinistre
                    if (date_sinis2!=None and date_sinis2!="")and (date_sinis1!=None and date_sinis1!=""):                   
                        diff=inter_dt(date_sinis1, date_sinis2)
                        if ((diff!=None) and (diff<=365)):
                            Rate=5
                            A=j
                            R="5%: l'immatriculation adverse a déjà fait l'objet d'un sinistre il y'a moins de 12 mois "+str(j.Dossier)
                            
                            break
                        
        Veoservices.objects.filter(Dossier=self.Dossier).update(R7=R)                   
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
                    if 0<=diff_sous_sinis<=30:
                        Rate=5  
                        R="5%: La  garantie  est Tierce  et il reste moins  d'un mois avant la fin  de  validité  de  contrat: "+self.Date_validité_fin
                else:
                    DFP=None
                    date_sinis=None
        Veoservices.objects.filter(Dossier=self.Dossier).update(R9=R)   
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
                
        Veoservices.objects.filter(Dossier=self.Dossier).update(R8=R)   
        return Rate






    
