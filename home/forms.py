from django import forms
from django.forms.widgets import Widget
from .models import *
import os

class ReviewForm(forms.ModelForm):
    rate=forms.IntegerField()
    class Meta:
        model=Reviews
        fields=["review","rate"]

    def clean_rate(self):
        rate= self.cleaned_data.get("rate")
        if not 5 >= rate >= 1:
            raise forms.ValidationError("invalid rate")
        return rate

PAYMENTS=(
    ("Bank Transaction","Bank Transaction"),
    ("Western Union","Western Union"),
    ("Vodafone Cash","Vodafone Cash"),
  
)
class PaymentMethodForm(forms.Form):
    payment_method=forms.ChoiceField(choices=PAYMENTS)
    image=forms.ImageField(label="Transaction Screenshot")
    number=forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Your Transaction Number ID"}),label="Transaction Number")

    def clean(self):
        try:
            image=self.cleaned_data.get("image")
            size=image.size / (1024 * 1024)
            type=os.path.splitext(image.name)[1]
            print(size)
            list_type=[".jpg",".jpeg",".png"]
            if size > 2:
                raise forms.ValidationError("image size is more 2 MB")
            elif type not in list_type:   
                raise forms.ValidationError(f"image Extension Must be JPG / JPEG / PNG")
        except:
            raise forms.ValidationError(f"invalid image")

    # def __init__(self,*args,**kwargs):
    #     super(PaymentMethodForm, self).__init__(*args, **kwargs)
        
    #     if "payment_method" in self.data:
    #         if self.data["payment_method"] == "Vodafone Cash":
    #             print("asdasd")
    #             self.fields['payment_method'].widget = forms.HiddenInput()
        # print(self.data)
        # self.fields["category"].queryset = Type_Child.objects.none()
        # if self.data["payment_method"] == "Paypal":
        #     print("here")
            # self.fields["branch"].queryset = Branch.objects.none()
            # print(self.data)

        # if self.data["type"] == None:
        #     print(self.data["type"],"hi")
        #     self.fields["category"].queryset = Type_Child.objects.filter(type=None) 
       
    
        # elif "category" in self.data:
            # # print(self.data["category"])
            # if self.data["category"] == "":
            #     self.fields["category"].queryset = Branch.objects.none()

            # else:
            #     self.fields["branch"].queryset = Branch.objects.filter(name__id=self.data["category"])

