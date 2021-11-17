from django import forms
from .models import Blog,Blog_Comment,Blog_Comment_Reply



class CommentForm(forms.ModelForm):
    class Meta:
        model=Blog_Comment
        fields=["comment"]
class ReplyForm(forms.ModelForm):
    class Meta:
        model=Blog_Comment_Reply
        fields=["reply"]
