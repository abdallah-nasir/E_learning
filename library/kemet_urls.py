from django.urls import path,include
from . import views 
from .views import *
from . import audio
app_name="library"
urlpatterns = [
#### movies 
    path("",views.home,name="home"),
    path("search/",views.search,name="all_search"),

    path("books/<str:slug>/",views.books,name="books"),
    path("movies/",views.movies,name="movies"),
    path("movies/<str:slug>/",views.single_movie,name="single_movie"),
    path("show/movie/<str:slug>/",views.show_movie,name="show_movie"),
    path("movie/<str:slug>/payment/",views.movie_payment,name="movie_payment"),
    path("paypal/create/<int:id>/",views.paypal_create,name="paypal_create"),
    path("paypal/capture/<str:order_id>/<str:movie_id>/",views.paypal_capture,name="paypal_capture"),
    path("western/create/<str:slug>/",views.create_movie_western_payment,name="movie_western_payment"),
    path("bank/create/<str:slug>/",views.create_movie_bank_payment,name="movie_bank_payment"),


#comments
    path("comments/create/<str:slug>/",views.create_movies_comment,name="create_movies_comment"),

####### audios
    path("music/",audio.home,name="audio_home"),
    path("music/releases/",audio.audio,name="audio"),
    path("music/track/<str:slug>/",audio.single_audio,name="single_audio"),
    path("music/artists/",audio.artists,name="artists"),
    path("music/artist/<str:slug>/",audio.single_artist,name="single_artist"),
    path("music/blogs/",audio.blog_audios,name="blogs"),
    path("music/search/",audio.search,name="search"),
    path("music/payment/<str:slug>/",audio.audio_payment,name="audio_payment"), 
    path("music/western/payment/<str:slug>/",audio.create_audio_western_payment,name="music_western_payment"),
    path("music/bank/payment/<str:slug>/",audio.create_audio_bank_payment,name="music_bank_payment"),

    path("music/paypal/create/<int:id>/",audio.paypal_create,name="audio_paypal_create"),
    path("music/paypal/capture/<str:order_id>/<int:track_id>/",audio.paypal_capture,name="audio_paypal_capture"),
    # path("msuic/paypal/create/<str:order_id>/<int:id>/",audio.paypal_create,name="paypal_create"),
    path("msuic/comments/create/<str:slug>/",audio.comment,name="comment"),
    path("audio-books/",include("library.audio_book_urls",namespace="audio_book")),
    path("e-books/",include("library.e_book_urls",namespace="e_book")),


]