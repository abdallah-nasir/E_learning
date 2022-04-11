from django.urls import path,include
from . import audios
app_name="Dashboard"

urlpatterns = [
path("add/track/",audios.add_track,name="add_track"), 
path("tracks/",audios.tracks,name="tracks"), 
path("demo/music/<str:slug>/",audios.track_music,name="track_music"), 
path("track/<str:slug>/",audios.single_track,name="single_track"), 
path("add/music/",audios.add_audio,name="add_audio"),  
path("edit/music/<str:slug>/",audios.edit_audio,name="edit_audio"), 
path("upload/music/<str:slug>/",audios.upload_music,name="upload_music"), 
path("delete/music/<str:slug>/",audios.delete_audio,name="delete_audio"), 
path("check/music/<str:slug>/",audios.check_audio,name="check_audio"), 
path("payment/",audios.audio_payment,name="audio_payment"), 
path("payment/edit/<int:id>/<str:slug>/",audios.edit_music_payment,name="edit_music_payment"), 
path("payment/refund/<int:id>/<str:slug>/",audios.music_refund,name="music_refund"), 
path("add/artist/",audios.artist_add,name="artist_add"), 
path("is-play-music/<str:slug>/",audios.is_play_music,name="is_play_music"), 


]  
