from allauth.account.signals import user_logged_in
from allauth.socialaccount.signals import pre_social_login
from django.contrib.auth.signals import user_logged_out  
from django.dispatch import receiver
from .models import *

@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    LoggedInUser.objects.get_or_create(user=kwargs.get('user')) 


@receiver(user_logged_out)
def on_user_logged_out(sender, **kwargs):
    LoggedInUser.objects.filter(user=kwargs.get('user')).delete()