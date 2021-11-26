from django import forms
from .models import Blog,Blog_Comment,Blog_Comment_Reply
from home.forms import PaymentMethodForm


class CommentForm(forms.ModelForm):
    class Meta:
        model=Blog_Comment
        fields=["comment"]
class ReplyForm(forms.ModelForm):
    class Meta:
        model=Blog_Comment_Reply
        fields=["reply"]

class PaymentForm(PaymentMethodForm):
    def __init__(self,*args,**kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)