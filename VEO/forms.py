from django.forms import ModelForm
from .models import Veoservices

class observationForm(ModelForm):
    class Meta:
        model = Veoservices
        fields = ['observation','statutdoute']


