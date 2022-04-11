from django import forms
from .models import *
from home.forms import PaymentMethodForm

PAYMENT=(
    ("credit","credit"),
     ("paypal","paypal"),
("western","western"),
     )
class CosultantForm(forms.Form):
    full_name=forms.CharField(required=True,max_length=50)
    specialization=forms.CharField(required=True,max_length=50)
    email=forms.EmailField(required=True,max_length=100)
    phone=forms.CharField(required=True,max_length=20)
    topic=forms.CharField(required=True,widget=forms.TextInput())
    terms=forms.BooleanField(required=True)
    method=forms.ChoiceField(required=True,choices=PAYMENT)
    date=forms.CharField(required=True)
    consultant=forms.IntegerField(required=True)
class PaymentForm(PaymentMethodForm):
    def __init__(self,*args,**kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)