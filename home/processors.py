from .models import Wishlist,Course,News
from django.core.cache import cache

def global_wishlist(request):
    if request.user.is_authenticated:
        my_wishlist,created=Wishlist.objects.get_or_create(user=request.user)
        # my_wishlist=cache.set("my_wishlist",my_wishlist,Never)
    else:
        my_wishlist=None
    message={"my_wishlist":my_wishlist}
    return message


def global_news(request):
    news=News.objects.all()
    message={"news":news}
    return message