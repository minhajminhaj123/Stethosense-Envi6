from . import views
from django.urls import path
from django.contrib.auth import views as authentication_views

app_name = 'patient'
urlpatterns = [
    path('Medications/', views.medications, name='medications'),
    path('LabReports/', views.labreports, name='labreports'),
    path('patientProfile/', views.patientProfile, name='patientProfile'),
    path('patientRecords/', views.patientRecords, name='patientRecords'),
    path('createPatientProfile/',views.create_patientprofile,name ='create_patientprofile'),
    path('patientvitals/',views.patientvitals_input,name ='patientvitals_input'),
    path('patientRegister/',views.patientRegister,name = 'patientRegister'),
    path('editPatient/',views.editPatient,name = 'editPatient'),
    path('editPatientVitals/',views.editPatientVitals,name = 'editPatientVitals'),
    path('addLabReports/',views.addLabReports,name = 'addLabReports'),
    path('logout/', authentication_views.LogoutView.as_view(template_name='centralapp/logout.html'), name='logout'),   
    # path('patLogin/', auth_views.login, {'template_name': 'patient/login.html'}, name = 'login'),
    # path('login/',authentication_views.LoginView.as_view(template_name='patient/patlogin.html'),name='patLogin'),
    # path('patLogout/',authentication_views.LogoutView.as_view(template_name='patient/patlogout.html'),name='patLogout'),
]
