from django import forms
from .models import *
from home.forms import PaymentMethodForm

class PaymentForm(PaymentMethodForm):
    def __init__(self,*args,**kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)


class CommentsForm(forms.ModelForm):
    comment=forms.CharField(required=True,max_length=100)
    class Meta:
        model=Comments
        fields=["comment"]