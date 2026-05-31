from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from core.models import Patient, NurseProfile, FoodItem, EducationModule
from .services.food_import_service import FoodImportService

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser, login_url='login')
def dashboard(request):
    context = {
        'total_patients': Patient.objects.filter(is_active=True).count(),
        'total_nurses': NurseProfile.objects.count(),
        'total_foods': FoodItem.objects.filter(is_active=True).count(),
        'total_modules': EducationModule.objects.count(),
        'latest_patient': Patient.objects.filter(is_active=True).order_by('-id').first(),
        'latest_nurse': NurseProfile.objects.order_by('-id').first(),
        'latest_food': FoodItem.objects.filter(is_active=True).order_by('-id').first(),
        'nav_active': 'dashboard'
    }
    return render(request, 'admin_portal/dashboard.html', context)

# ----------------- Patients -----------------
@user_passes_test(is_superuser, login_url='login')
def patient_list(request):
    q = request.GET.get('q', '').strip()
    patients = Patient.objects.filter(is_active=True)
    if q:
        patients = patients.filter(
            Q(full_name__icontains=q) | 
            Q(patient_code__icontains=q)
        )
    return render(request, 'admin_portal/patients/list.html', {'patients': patients, 'q': q, 'nav_active': 'patients'})

@user_passes_test(is_superuser, login_url='login')
def patient_create(request):
    if request.method == 'POST':
        patient_code = request.POST.get('patient_code')
        full_name = request.POST.get('full_name')
        age = request.POST.get('age') or 0
        ward = request.POST.get('ward', 'Ward A')
        bed = request.POST.get('bed', '')
        status = request.POST.get('status', 'stable')
        
        Patient.objects.create(
            patient_code=patient_code,
            full_name=full_name,
            age=age,
            ward=ward,
            bed=bed,
            status=status
        )
        messages.success(request, 'Patient created successfully.')
        return redirect('admin_patient_list')
        
    return render(request, 'admin_portal/patients/form.html', {'nav_active': 'patients'})

@user_passes_test(is_superuser, login_url='login')
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'admin_portal/patients/detail.html', {'patient': patient, 'nav_active': 'patients'})

@user_passes_test(is_superuser, login_url='login')
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        patient.patient_code = request.POST.get('patient_code')
        patient.full_name = request.POST.get('full_name')
        patient.age = request.POST.get('age') or 0
        patient.ward = request.POST.get('ward', 'Ward A')
        patient.bed = request.POST.get('bed', '')
        patient.status = request.POST.get('status', 'stable')
        patient.save()
        
        messages.success(request, 'Patient updated successfully.')
        return redirect('admin_patient_list')
        
    return render(request, 'admin_portal/patients/form.html', {'patient': patient, 'nav_active': 'patients'})

@user_passes_test(is_superuser, login_url='login')
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        patient.is_active = False
        patient.save()
        messages.success(request, 'Patient deleted successfully.')
        return redirect('admin_patient_list')
        
    return render(request, 'admin_portal/patients/delete.html', {'patient': patient, 'nav_active': 'patients'})

# ----------------- Nurses -----------------
@user_passes_test(is_superuser, login_url='login')
def nurse_list(request):
    q = request.GET.get('q', '').strip()
    nurses = NurseProfile.objects.all()
    if q:
        nurses = nurses.filter(
            Q(user__first_name__icontains=q) |
            Q(user__email__icontains=q) |
            Q(employee_id__icontains=q)
        )
    return render(request, 'admin_portal/nurses/list.html', {'nurses': nurses, 'q': q, 'nav_active': 'nurses'})

@user_passes_test(is_superuser, login_url='login')
def nurse_create(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        ward = request.POST.get('ward', 'Ward A')
        title = request.POST.get('title', 'Nurse')
        password = request.POST.get('password')
        
        user = User.objects.create_user(username=employee_id, email=email, password=password, first_name=first_name, last_name=last_name)
        NurseProfile.objects.create(user=user, employee_id=employee_id, ward=ward, title=title)
        
        messages.success(request, 'Nurse profile created successfully.')
        return redirect('admin_nurse_list')
        
    return render(request, 'admin_portal/nurses/form.html', {'nav_active': 'nurses'})

@user_passes_test(is_superuser, login_url='login')
def nurse_edit(request, pk):
    nurse = get_object_or_404(NurseProfile, pk=pk)
    
    if request.method == 'POST':
        nurse.employee_id = request.POST.get('employee_id')
        nurse.ward = request.POST.get('ward', 'Ward A')
        nurse.title = request.POST.get('title', 'Nurse')
        nurse.save()
        
        user = nurse.user
        user.username = nurse.employee_id
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        
        messages.success(request, 'Nurse profile updated successfully.')
        return redirect('admin_nurse_list')
        
    return render(request, 'admin_portal/nurses/form.html', {'nurse': nurse, 'nav_active': 'nurses'})

@user_passes_test(is_superuser, login_url='login')
def nurse_delete(request, pk):
    nurse = get_object_or_404(NurseProfile, pk=pk)
    
    if request.method == 'POST':
        user = nurse.user
        nurse.delete()
        user.delete()
        messages.success(request, 'Nurse profile deleted successfully.')
        return redirect('admin_nurse_list')
        
    return render(request, 'admin_portal/nurses/delete.html', {'nurse': nurse, 'nav_active': 'nurses'})

@user_passes_test(is_superuser, login_url='login')
def nurse_reset_password(request, pk):
    nurse = get_object_or_404(NurseProfile, pk=pk)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if new_password:
            nurse.user.set_password(new_password)
            nurse.user.save()
            messages.success(request, 'Password reset successfully.')
            return redirect('admin_nurse_list')
            
    return render(request, 'admin_portal/nurses/reset_password.html', {'nurse': nurse, 'nav_active': 'nurses'})

# ----------------- Foods -----------------
@user_passes_test(is_superuser, login_url='login')
def food_list(request):
    q = request.GET.get('q', '').strip()
    foods = FoodItem.objects.filter(is_active=True)
    if q:
        foods = foods.filter(Q(name__icontains=q))
    return render(request, 'admin_portal/foods/list.html', {'foods': foods, 'q': q, 'nav_active': 'foods'})

@user_passes_test(is_superuser, login_url='login')
def food_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        calories = request.POST.get('calories') or 0
        protein = request.POST.get('protein') or 0
        sodium = request.POST.get('sodium') or 0
        potassium = request.POST.get('potassium') or 0
        phosphorus = request.POST.get('phosphorus') or 0
        fluid = request.POST.get('estimated_fluid_ml') or 0
        hd_status = request.POST.get('hd_status', 'aman')
        description = request.POST.get('description', '')
        image = request.FILES.get('image')
        
        food = FoodItem.objects.create(
            name=name,
            calories=calories,
            protein=protein,
            sodium=sodium,
            potassium=potassium,
            phosphorus=phosphorus,
            estimated_fluid_ml=fluid,
            hd_status=hd_status,
            description=description
        )
        
        if image:
            food.image = image
            food.save()
            
        messages.success(request, 'Food item created successfully.')
        return redirect('admin_food_list')
        
    return render(request, 'admin_portal/foods/form.html', {'nav_active': 'foods'})

@user_passes_test(is_superuser, login_url='login')
def food_detail(request, pk):
    food = get_object_or_404(FoodItem, pk=pk)
    return render(request, 'admin_portal/foods/detail.html', {'food': food, 'nav_active': 'foods'})

@user_passes_test(is_superuser, login_url='login')
def food_edit(request, pk):
    food = get_object_or_404(FoodItem, pk=pk)
    
    if request.method == 'POST':
        food.name = request.POST.get('name')
        food.calories = request.POST.get('calories') or 0
        food.protein = request.POST.get('protein') or 0
        food.sodium = request.POST.get('sodium') or 0
        food.potassium = request.POST.get('potassium') or 0
        food.phosphorus = request.POST.get('phosphorus') or 0
        food.estimated_fluid_ml = request.POST.get('estimated_fluid_ml') or 0
        food.hd_status = request.POST.get('hd_status', 'aman')
        food.description = request.POST.get('description', '')
        
        if 'image' in request.FILES:
            food.image = request.FILES['image']
            
        food.save()
        
        messages.success(request, 'Food item updated successfully.')
        return redirect('admin_food_detail', pk=food.pk)
        
    return render(request, 'admin_portal/foods/form.html', {'food': food, 'nav_active': 'foods'})

@user_passes_test(is_superuser, login_url='login')
def food_delete(request, pk):
    food = get_object_or_404(FoodItem, pk=pk)
    
    if request.method == 'POST':
        food.is_active = False
        food.save()
        messages.success(request, 'Food item deleted successfully.')
        return redirect('admin_food_list')
        
    return render(request, 'admin_portal/foods/delete.html', {'food': food, 'nav_active': 'foods'})

@user_passes_test(is_superuser, login_url='login')
def food_import(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, 'Please select a file to upload.')
            return redirect('admin_food_import')
            
        file = request.FILES['file']
        if not (file.name.endswith('.csv') or file.name.endswith('.xls') or file.name.endswith('.xlsx')):
            messages.error(request, 'Unsupported file format. Please upload CSV, XLS, or XLSX.')
            return redirect('admin_food_import')
            
        try:
            result = FoodImportService.import_file(file)
            messages.success(request, f"Import Completed! Total Rows: {result['total']}, Created: {result['created']}, Updated: {result['updated']}, Skipped: {result['skipped']}")
            return redirect('admin_food_list')
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
            return redirect('admin_food_import')

    return render(request, 'admin_portal/foods/import.html', {'nav_active': 'foods'})

# ----------------- Education Modules -----------------
@user_passes_test(is_superuser, login_url='login')
def education_list(request):
    q = request.GET.get('q', '').strip()
    modules = EducationModule.objects.all()
    if q:
        modules = modules.filter(Q(title__icontains=q))
    return render(request, 'admin_portal/education_modules/list.html', {'modules': modules, 'q': q, 'nav_active': 'education'})

@user_passes_test(is_superuser, login_url='login')
def education_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        sort_order = request.POST.get('sort_order') or 0
        is_published = request.POST.get('is_published') == 'on'
        
        module = EducationModule.objects.create(
            title=title,
            content=content,
            sort_order=sort_order,
            is_published=is_published
        )
        
        if 'thumbnail' in request.FILES:
            module.thumbnail = request.FILES['thumbnail']
            module.save()
            
        messages.success(request, 'Education module created successfully.')
        return redirect('admin_education_list')
        
    return render(request, 'admin_portal/education_modules/form.html', {'nav_active': 'education'})

@user_passes_test(is_superuser, login_url='login')
def education_detail(request, pk):
    module = get_object_or_404(EducationModule, pk=pk)
    return render(request, 'admin_portal/education_modules/detail.html', {'module': module, 'nav_active': 'education'})

@user_passes_test(is_superuser, login_url='login')
def education_edit(request, pk):
    module = get_object_or_404(EducationModule, pk=pk)
    
    if request.method == 'POST':
        module.title = request.POST.get('title')
        module.content = request.POST.get('content')
        module.sort_order = request.POST.get('sort_order') or 0
        module.is_published = request.POST.get('is_published') == 'on'
        
        if 'thumbnail' in request.FILES:
            module.thumbnail = request.FILES['thumbnail']
            
        module.save()
        messages.success(request, 'Education module updated successfully.')
        return redirect('admin_education_list')
        
    return render(request, 'admin_portal/education_modules/form.html', {'module': module, 'nav_active': 'education'})

@user_passes_test(is_superuser, login_url='login')
def education_delete(request, pk):
    module = get_object_or_404(EducationModule, pk=pk)
    
    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Education module deleted successfully.')
        return redirect('admin_education_list')
        
    return render(request, 'admin_portal/education_modules/delete.html', {'module': module, 'nav_active': 'education'})

@user_passes_test(is_superuser, login_url='login')
def education_toggle_publish(request, pk):
    module = get_object_or_404(EducationModule, pk=pk)
    module.is_published = not module.is_published
    module.save()
    messages.success(request, f'Module "{"published" if module.is_published else "unpublished"}" successfully.')
    return redirect('admin_education_list')
