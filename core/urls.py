from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('alerts/', views.alerts_list, name='alerts'),
    path('alerts/<int:pk>/resolve/', views.alert_resolve, name='alert_resolve'),
]
