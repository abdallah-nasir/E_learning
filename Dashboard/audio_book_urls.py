from django.urls import path,include
from . import audio_book as views
app_name="Dashboard"
 
urlpatterns = [
path("add/track/",views.add_track,name="add_track"), 
path("tracks/",views.tracks,name="tracks"),
path("track/<str:slug>/",views.single_track,name="single_track"), 
path("add/music/",views.add_audio,name="add_audio"),  
path("upload/music/<str:slug>/",views.upload_music,name="upload_music"), 
path("edit/music/<str:slug>/",views.edit_audio,name="edit_audio"), 
path("is-play-music/<str:slug>/",views.is_play_music,name="is_play_music"), 
path("payments/",views.audio_payment,name="audio_payment"), 
path("refund/<str:slug>/<int:id>/",views.audio_book_refund,name="audio_book_refund"), 
path("edit/audio-book/payment/<str:slug>/<int:id>/",views.edit_audio_book_payment,name="edit_music_payment"), 
 path("demo/<str:slug>/",views.track_music,name="track_music"), 

 

]  
