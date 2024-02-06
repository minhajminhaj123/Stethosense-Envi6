from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib import messages
from .forms import DoctorRegisterForm, DoctorProfileForm
from django.contrib.auth.decorators import login_required
from .models import DoctorProfile
# from django.views import View
from .models import DoctorProfile,PatientDocConfig
from patient.models import PatientProfile,PatientVitals,LabReports,Records
import datetime
def doctorRegister(request):
    if request.method =='POST':
        form = DoctorRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # usertype = 2
            user.set_password(password)
            user.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('doctor:create_doctorprofile')
    else:
        form = DoctorRegisterForm()
    return render(request,'pages/doctorRegister.html', {'form':form})

@login_required
def create_doctorprofile(request):
    if request.method =='POST':
        form = DoctorProfileForm(request.POST)
        
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.doctor = request.user
            doctor.save()
            return redirect('doctor:doctorProfile')
        else:
            print("here1")
            
    else:
        print("here")
        form = DoctorProfileForm()
    return render(request,'pages/doctor-profile-create.html',{'form':form})


@login_required
def doctorProfile(request):
    profile = DoctorProfile.objects.get(doctor=request.user)

    return render(request, 'pages/doctor_profile.html',{'profile':profile})


@login_required
def PatientList(request):
    pats=PatientDocConfig.objects.filter(doctor_id=request.user.id)
    print(len(pats))

    patient_l=[]
    for p in pats:
        print("hello")
        patient_l.append(PatientProfile.objects.filter(access_code=p.access_code)[0])

    Patient_list=PatientProfile.objects.filter()
    print(len(patient_l))


    return render(request, 'pages/patientList.html',{'patientl':patient_l})


@login_required
def pat_profile(request,p):
    print(p)
    
   
   
    subject=PatientProfile.objects.filter(id=p)[0]
    pat_user=User.objects.get(id=subject.userid)
    
    pat_vitals=PatientVitals.objects.filter(patientv=pat_user)
    all_reports=Records.objects.filter(patient_id=p).order_by('id').reverse()
    
    all_lab=LabReports.objects.filter(patientl=pat_user).order_by('id').reverse()
    
    print(len(all_lab))
    print(len(pat_vitals))

    
    for report in all_reports:
        des=report.medication
        med=des.split(":")
        m_list=[]
        for m in med:
            dosage=m.split("/")
        m_list.append(dosage)

        report.medication=m_list
        
        
    return render(request,'pages/patient_records_in_doc.html',{'subject':subject,"vitals":pat_vitals.first(),'Reports':all_reports,"labreports":all_lab})

@login_required
def newReport(request,p):
    doctor=DoctorProfile.objects.filter(doctor=request.user)[0]
    patient=PatientProfile.objects.filter(id=p)[0]
    date=str(datetime.datetime.now()).split(" ")[0]

    obj={'doctor_name':doctor.name,'patient_name':patient.name,'date':date,"docid":doctor.id,"patid":patient.id}
    return render(request,'pages/report.html',{'details':obj})

@login_required
def addReport(request):
    if request.method=="POST":
        new_record=Records()
        new_record.date=str(datetime.datetime.now()).split(" ")[0]
        new_record.diagnosis=request.POST['diagnosis']
        new_record.doctor_name=request.POST['doctor_name']
        new_record.Symptoms=request.POST['symptoms']
        new_record.medication=request.POST['medication']
        new_record.patient_id=request.POST['patid']
        new_record.doctor_id=request.POST['docid']
        new_record.additional_precautions=request.POST['additional_precautions']
        new_record.save()
        addr='doctor:pat_profile/'+ str(request.POST['patid'])

        return redirect('/pat_profile/'+ str(request.POST['patid']))

@login_required
def addPatient(request):
    print("entered1")
    
    accesscode=request.POST['accesscode']
    print(accesscode)
    print("entered")
    if len(PatientProfile.objects.filter(access_code=accesscode))==0:
        return redirect('/PatientList/')
    else:
        print("heya")
        check_pat=PatientProfile.objects.filter(access_code=accesscode)[0]
        print(check_pat.access_code)
        
           
        new_config=PatientDocConfig()
            
        new_config.doctor_id=request.user.id
        new_config.access_code=accesscode
        new_config.save()
        return redirect('/PatientList/')
        
@login_required
def editdoctorprofile(request):
    doctor = get_object_or_404(DoctorProfile, doctor=request.user)
    # patient = PatientProfile.objects.get(patient=request.user)
    # if request.method == 'POST':
    form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
    # if request.method == 'POST':

    if form.is_valid():
        doctor = form.save(commit=False)
        doctor.doctor = request.user
        doctor.save()
        return redirect('doctor:doctorProfile')
    return render(request,'pages/doctor_profile_edit.html',{'form':form})