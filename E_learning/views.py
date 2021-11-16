
from django.http.response import FileResponse
from django.http import HttpResponseForbidden

def media_access(request, path):    
    access_granted = False

    user = request.user
    if user.is_authenticated():
        if user.is_staff:
            # If admin, everything is granted
            access_granted = True
        else:
            # For simple user, only their documents can be accessed
            doc = user.related_PRF_user.i_image  #Customize this...

            path = f"images/{path}"
            if path == doc:
                access_granted = True

    if access_granted:
        response = FileResponse(user.related_PRF_user.i_image)
        return response
    else:
        return HttpResponseForbidden('Not authorized to access this media.')