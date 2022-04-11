
from ast import While
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import redirect
from django.utils import translation
from django.urls import reverse
from django.utils.translation import get_language,get_language_info
from django.conf import settings
import urllib
def change_language(request):
    current_language=get_language()
    path=request.GET["path"]
    language=request.GET["language"]
    count=-1
    path_list=path.split("/")
    final_path=f"/{language}{path}"
    for i in settings.LANGUAGES:
        count +=1
        if settings.LANGUAGES[count][0] in path_list[:2]:
            index=path_list.index(settings.LANGUAGES[count][0])
            path_list[index]=language
            translation.activate(language) 
            final_path="/".join(path_list)
            break
    return redirect(final_path)
