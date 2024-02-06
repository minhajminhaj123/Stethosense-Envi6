from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .forms import PatientRegisterForm,PatientProfileForm,PatientVitalsForm
from django.contrib.auth.decorators import login_required
from .models import PatientProfile,PatientVitals,Records,LabReports
from django.contrib.auth import logout

def patientRegister(request):
    if request.method =='POST':
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            # form.save()
            # username = form.cleaned_data.get('username')
            # email = form.cleaned_data.get('email')
            # return redirect('login')
            user = form.save(commit=False)
            user.usertype= 1
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # email = form.cleaned_data['email']
            # user.AccessCode = hash(email)
            user.set_password(password)
            user.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('patient:create_patientprofile')
    else:
        form = PatientRegisterForm()
    return render(request,'patient/patientregister.html',{'form':form})

@login_required
def create_patientprofile(request):
    if request.method =='POST':
        form = PatientProfileForm(request.POST)
        if form.is_valid():

            patient = form.save(commit=False)
            # name = form.cleaned_data['name']
            # patient.AccessCode = hash(name)
            patient.patient = request.user
            patient.save()
            # form.patient = request.user
            # form.save()
            patient=PatientProfile.objects.filter(patient=request.user)[0]
            print(patient.address)
            print(hash(patient.address))
            patient.access_code=hash( str(patient.id) +patient.address)
            patient.userid=request.user.id ##changed
            patient.save()
            
            return redirect('patient:patientvitals_input')
    else:
        form = PatientProfileForm()
    return render(request,'patient/patient-profile-create.html',{'form':form})

@login_required
def patientvitals_input(request):
    if request.method =='POST':
        form = PatientVitalsForm(request.POST)
        if form.is_valid():
            patientv = form.save(commit=False)
            patientv.patientv = request.user
            patientv.save()
            # form.save()
            return redirect('patient:patientProfile')
    else:
        form = PatientVitalsForm()
    return render(request,'patient/patientvital_info.html',{'form':form})

 
@login_required
def patientProfile(request):
    profile = PatientProfile.objects.get(patient=request.user)
    return render(request, 'patient/patient_profile.html',{'profile':profile})

@login_required
def patientRecords(request):
    vitals = PatientVitals.objects.get(patientv=request.user)
    patient=PatientProfile.objects.filter(patient=request.user)[0]
    all_reports=list(Records.objects.filter(patient_id=patient.id).order_by('id').reverse())
    count=0
    rec=[]
    for r in all_reports:
        if count ==1:
            break
        rec.append(r)
        count=count+1


        for report in rec:
            des=report.medication
            med=des.split(":")
            m_list=[]
            for m in med:
	            dosage=m.split("/")
	            m_list.append(dosage)
            report.medication=m_list

    all_lab=LabReports.objects.filter(patientl=request.user).order_by('id').reverse()
    count=0
    current=[]
    for lab in all_lab:
        if count==1:
            break
        current.append(lab)
        count=count+1

    return render(request, 'patient/patient_records.html',{'vitals':vitals,'Reports':rec,"lab_rec":current})

@login_required 
def labreports(request):
    all_lab=LabReports.objects.filter(patientl=request.user)
    print(request.user.id)

    return render(request, 'patient/labreports.html',{"reports":all_lab})


@login_required
def addLabReports(request):
    if request.method=="POST":
        new_report=LabReports()
        new_report.patientl=request.user
        new_report.report_name=request.POST['report_name']
        new_report.report_date=request.POST['report_date']
        new_report.labreportfile=request.FILES['file']
        new_report.save()

        return redirect('patient:labreports')
    else:
        return redirect('patient:labreports')




@login_required
def medications(request):
    patient=PatientProfile.objects.filter(patient=request.user)[0]
    all_reports=Records.objects.filter(patient_id=patient.id).order_by('id').reverse()
    
    print(len(all_reports.reverse()))
    for report in all_reports:
        des=report.medication
        med=des.split(":")
        m_list=[]
        for m in med:
	        dosage=m.split("/")
	        m_list.append(dosage)

        report.medication=m_list
        

    return render(request, 'patient/medications.html',{'Reports':all_reports})

@login_required
def editPatient(request):
    patient = get_object_or_404(PatientProfile, patient=request.user)
    # patient = PatientProfile.objects.get(patient=request.user)
    # if request.method == 'POST':
    form = PatientProfileForm(request.POST, request.FILES, instance=patient)
    # if request.method == 'POST':

    if form.is_valid():
        patient = form.save(commit=False)
        patient.patient = request.user
        patient.save()
        return redirect('patient:patientProfile')
    # else:
    #     form = PatientProfileForm()
    return render(request,'patient/patient-profile-edit.html',{'form':form})

@login_required
def editPatientVitals(request):
    patientv = get_object_or_404(PatientVitals, patientv=request.user)
    # if request.method == 'POST':
    form = PatientVitalsForm(request.POST, request.FILES, instance=patientv)
    if form.is_valid():
        patientv = form.save(commit=False)
        patientv.patientv = request.user
        patientv.save()
        return redirect('patient:patientRecords')
    # else:
        # form = PatientVitalsForm()
    return render(request,'patient/patient-vitals-edit.html',{'form':form})

