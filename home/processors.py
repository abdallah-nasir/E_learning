from .models import Wishlist,Course
from django.core.cache import cache
def global_wishlist(request):
    if request.user.is_authenticated:
      
        my_wishlist,created=Wishlist.objects.get_or_create(user=request.user)
    else:
        my_wishlist=None
    message={"my_wishlist":my_wishlist}
    return message