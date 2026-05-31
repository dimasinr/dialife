from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    
    # Patients
    path('patients/', views.patient_list, name='admin_patient_list'),
    path('patients/add/', views.patient_create, name='admin_patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='admin_patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_edit, name='admin_patient_edit'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='admin_patient_delete'),
    
    # Nurses
    path('nurses/', views.nurse_list, name='admin_nurse_list'),
    path('nurses/add/', views.nurse_create, name='admin_nurse_create'),
    path('nurses/<int:pk>/edit/', views.nurse_edit, name='admin_nurse_edit'),
    path('nurses/<int:pk>/delete/', views.nurse_delete, name='admin_nurse_delete'),
    path('nurses/<int:pk>/reset-password/', views.nurse_reset_password, name='admin_nurse_reset_password'),
    
    # Foods
    path('foods/', views.food_list, name='admin_food_list'),
    path('foods/add/', views.food_create, name='admin_food_create'),
    path('foods/<int:pk>/', views.food_detail, name='admin_food_detail'),
    path('foods/<int:pk>/edit/', views.food_edit, name='admin_food_edit'),
    path('foods/<int:pk>/delete/', views.food_delete, name='admin_food_delete'),
    path('foods/import/', views.food_import, name='admin_food_import'),
    
    # Education Modules
    path('education-modules/', views.education_list, name='admin_education_list'),
    path('education-modules/add/', views.education_create, name='admin_education_create'),
    path('education-modules/<int:pk>/', views.education_detail, name='admin_education_detail'),
    path('education-modules/<int:pk>/edit/', views.education_edit, name='admin_education_edit'),
    path('education-modules/<int:pk>/delete/', views.education_delete, name='admin_education_delete'),
    path('education-modules/<int:pk>/toggle-publish/', views.education_toggle_publish, name='admin_education_toggle_publish'),
]
