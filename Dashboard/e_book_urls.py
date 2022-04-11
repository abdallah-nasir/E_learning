from django.urls import path,include
from . import e_book as views
app_name="Dashboard"
  
urlpatterns = [
path("add/book/",views.add_e_book,name="add_e_book"), 
path("books/",views.books,name="books"),
path("upload/pdf/<str:slug>/",views.upload_pdf,name="upload_pdf"), 
path("edit/book/<str:slug>/",views.edit_book,name="edit_book"), 

# path("track/<str:slug>/",views.single_track,name="single_track"), 
# path("add/music/",views.add_audio,name="add_audio"),  
# path("is-play-music/<str:slug>/",views.is_play_music,name="is_play_music"), 
# path("payments/",views.audio_payment,name="audio_payment"), 
# path("refund/<str:slug>/<int:id>/",views.audio_book_refund,name="audio_book_refund"), 
# path("edit/audio-book/payment/<str:slug>/<int:id>/",views.edit_audio_book_payment,name="edit_music_payment"), 
#  path("demo/<str:slug>/",views.track_music,name="track_music"), 

 

]  
