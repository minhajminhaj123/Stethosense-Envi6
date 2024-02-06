from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as authentication_views

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', include('home.urls')),
    path('', include('patient.urls')),
    path('', include('doctor.urls')),
    path('', include('centralapp.urls')),
    path('login/', authentication_views.LoginView.as_view(template_name='centralapp/login.html'), name='login'), 
    
] 

from django.conf import settings 
from django.conf.urls.static import static 

urlpatterns += [ 
    # ... the rest of your URLconf goes here ... 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)