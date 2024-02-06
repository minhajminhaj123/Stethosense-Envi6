from . import views
from django.urls import path
from django.contrib.auth import views as authentication_views

app_name = 'doctor'
urlpatterns = [
    path('doctorProfile/', views.doctorProfile, name='doctorProfile'),
    path('createDoctorProfile/',views.create_doctorprofile,name ='create_doctorprofile'),
    path('doctorRegister/',views.doctorRegister,name = 'doctorRegister'),
    path('PatientList/',views.PatientList,name = 'PatientList'),
    path('pat_profile/<int:p>', views.pat_profile,name = 'pat_profile'),
    path('newReport/<int:p>',views.newReport,name="newReport"),
    path('addReport/',views.addReport,name="addReport"),
    path('addPatient/',views.addPatient,name="addPatient"),
    path('editdocprofile/',views.editdoctorprofile,name="editdoctorprofile"),

    # path('logout/', authentication_views.LogoutView.as_view(template_name='centralapp/logout.html'), name='logout'),
    # path('mypatients',views.mypatients,name = "mypatients"),
    # path('editDoctor/',views.editDoctor,name = 'editDoctor'),
]

