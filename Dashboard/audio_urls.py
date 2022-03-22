from django.urls import path,include
from . import audios
app_name="Dashboard"

urlpatterns = [
path("add/track/",audios.add_track,name="add_track"), 
path("tracks/",audios.tracks,name="tracks"), 
path("track/<str:slug>/",audios.single_track,name="single_track"), 
path("add/music/",audios.add_audio,name="add_audio"), 
path("upload/music/<str:slug>/",audios.upload_music,name="upload_music"), 
path("delete/music/<str:slug>/",audios.delete_audio,name="delete_audio"), 
path("check/music/<str:slug>/",audios.check_audio,name="check_audio"), 
path("payment/",audios.audio_payment,name="audio_payment"), 

]  
