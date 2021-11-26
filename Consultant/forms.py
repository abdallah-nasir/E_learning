from django import forms
from .models import *
from home.forms import PaymentMethodForm

class CosultantForm(forms.ModelForm):
    name=forms.ModelChoiceField(queryset=Category.objects.all(),label="Category")
    teacher=forms.ModelChoiceField(required=False,queryset=Teacher_Time.objects.none(),label="Teacher")
    date=forms.DateTimeInput()
    class Meta:
        model=Category 
        fields=['name']
    def __init__(self,*args,**kwargs):
        super(CosultantForm, self).__init__(*args, **kwargs)
        if "category" in self.data:
            category=self.data["category"]
            print(category)
            self.fields["teacher"].required = True

class PaymentForm(PaymentMethodForm):
    def __init__(self,*args,**kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)