from django.urls import path,include
from . import views 
from .views import *
from . import audio
app_name="library"
urlpatterns = [
#### movies
    path("",views.home,name="home"),
    path("movies/",views.movies,name="movies"),
    path("movies/<str:slug>/",views.single_movie,name="single_movie"),
    path("show/movie/<str:slug>/",views.show_movie,name="show_movie"),
    path("movie/<str:slug>/payment/",views.movie_payment,name="movie_payment"),
    path("paypal/create/<int:id>/",views.paypal_create,name="paypal_create"),
    path("paypal/capture/<str:order_id>/<str:movie_id>/",views.paypal_capture,name="paypal_capture"),
    path("paymob/<int:id>/",views.paymob_payment,name="paymob_payment"),
    path("capture/paymob/<int:id>/",views.paymob_payment,name="paymob_payment"),
    path("western/create/<str:slug>/",views.create_movie_western_payment,name="create_movie_western_payment"),

#comments
    path("comments/create/<str:slug>/",views.create_movies_comment,name="create_movies_comment"),

####### audios
    path("msuic/",audio.home,name="audio_home"),
    path("msuic/releases/",audio.audio,name="audio"),
    path("msuic/track/<str:slug>/",audio.single_audio,name="single_audio"),
    path("msuic/artists/",audio.artists,name="artists"),
    path("msuic/artist/<str:slug>/",audio.single_artist,name="single_artist"),
    path("msuic/blogs/",audio.blog_audios,name="blogs"),
    path("msuic/search/",audio.search,name="search"),
    path("msuic/payment/<str:slug>/",audio.audio_payment,name="audio_payment"),
    path("msuic/western/payment/<str:slug>/",audio.create_audio_western_payment,name="create_audio_western_payment"),
    path("msuic/paypal/create/<int:id>/",audio.paypal_create,name="audio_paypal_create"),
    path("msuic/paypal/capture/<str:order_id>/<int:track_id>/",audio.paypal_capture,name="audio_paypal_capture"),
    path("msuic/paymob/<int:id>/",audio.paymob_payment,name="audio_paymob_payment"),
 
    
    # path("msuic/paypal/create/<str:order_id>/<int:id>/",audio.paypal_create,name="paypal_create"),

    path("msuic/comments/create/<str:slug>/",audio.comment,name="comment"),

]