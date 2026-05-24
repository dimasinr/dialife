from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Alert, AlertSeverity, FluidLog, Patient, PatientStatus, VitalReading


def _nurse_context(request):
    profile = getattr(request.user, 'nurse_profile', None)
    return {
        'nurse_name': request.user.get_full_name() or request.user.username,
        'nurse_ward': profile.ward if profile else 'Clinical Unit',
        'nurse_title': profile.title if profile else 'Nurse',
        'nurse_avatar': profile.avatar_url if profile else '',
        'active_alert_count': Alert.objects.filter(is_resolved=False).count(),
    }


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=employee_id, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Employee ID atau password tidak valid.')

    return render(request, 'auth/login.html')


@login_required(login_url='login')
def logout_view(request):
    auth_logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    patients = Patient.objects.filter(is_active=True)
    alerts_qs = Alert.objects.filter(is_resolved=False).select_related('patient')[:8]
    critical_count = patients.filter(status=PatientStatus.CRITICAL).count()
    context = {
        **_nurse_context(request),
        'nav_active': 'dashboard',
        'page_title': 'Nurse Dashboard',
        'total_patients': patients.count(),
        'active_alerts': Alert.objects.filter(is_resolved=False).count(),
        'critical_alerts': Alert.objects.filter(
            is_resolved=False,
            severity=AlertSeverity.CRITICAL,
        ).count(),
        'recent_alerts': alerts_qs,
        'patients': patients[:10],
    }
    return render(request, 'dashboard/index.html', context)


@login_required(login_url='login')
def patient_list(request):
    qs = Patient.objects.filter(is_active=True)
    status = request.GET.get('status', '')
    ward = request.GET.get('ward', '')
    q = request.GET.get('q', '').strip()

    if status:
        qs = qs.filter(status=status)
    if ward:
        qs = qs.filter(ward=ward)
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q)
            | Q(patient_code__icontains=q)
            | Q(bed__icontains=q)
        )

    wards = Patient.objects.values_list('ward', flat=True).distinct().order_by('ward')
    context = {
        **_nurse_context(request),
        'nav_active': 'patients',
        'page_title': 'Patient Monitoring Overview',
        'patients': qs,
        'total_patients': Patient.objects.filter(is_active=True).count(),
        'critical_count': Patient.objects.filter(
            is_active=True,
            status=PatientStatus.CRITICAL,
        ).count(),
        'wards': wards,
        'filter_status': status,
        'filter_ward': ward,
        'search_query': q,
    }
    return render(request, 'monitoring_patiens/index.html', context)


@login_required(login_url='login')
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk, is_active=True)
    latest_vital = patient.vitals.first()
    fluid_logs = patient.fluid_logs.all()[:20]
    trend_logs = (
        FluidLog.objects.filter(patient=patient)
        .order_by('-logged_at')[:7]
    )
    active_alert = patient.alerts.filter(is_resolved=False).first()
    intake_today = sum(
        log.volume_ml
        for log in patient.fluid_logs.filter(
            category__in=['drink', 'food'],
            logged_at__date=timezone.localdate(),
        )
    )
    output_today = sum(
        log.volume_ml
        for log in patient.fluid_logs.filter(
            category='urine',
            logged_at__date=timezone.localdate(),
        )
    )
    context = {
        **_nurse_context(request),
        'nav_active': 'patients',
        'page_title': f'Patient Monitoring — {patient.full_name}',
        'patient': patient,
        'vital': latest_vital,
        'fluid_logs': fluid_logs,
        'trend_logs': trend_logs,
        'active_alert': active_alert,
        'intake_today': intake_today or patient.fluid_intake_today_ml,
        'output_today': output_today,
        'fluid_percent': patient.fluid_percent,
    }
    return render(request, 'monitoring_patiens/detail_patiens.html', context)


@login_required(login_url='login')
def alerts_list(request):
    qs = Alert.objects.select_related('patient', 'resolved_by')
    severity = request.GET.get('severity', '')
    q = request.GET.get('q', '').strip()
    show_resolved = request.GET.get('resolved') == '1'

    if not show_resolved:
        qs = qs.filter(is_resolved=False)
    if severity:
        qs = qs.filter(severity=severity)
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(message__icontains=q)
            | Q(patient__full_name__icontains=q)
            | Q(patient__patient_code__icontains=q)
        )

    context = {
        **_nurse_context(request),
        'nav_active': 'alerts',
        'page_title': 'Alerts & History Log',
        'alerts': qs,
        'critical_count': Alert.objects.filter(
            is_resolved=False,
            severity=AlertSeverity.CRITICAL,
        ).count(),
        'filter_severity': severity,
        'search_query': q,
        'show_resolved': show_resolved,
    }
    return render(request, 'alerts/index.html', context)


@login_required(login_url='login')
def alert_resolve(request, pk):
    if request.method != 'POST':
        return redirect('alerts')
    alert = get_object_or_404(Alert, pk=pk)
    alert.is_resolved = True
    alert.resolved_at = timezone.now()
    alert.resolved_by = request.user
    alert.save(update_fields=['is_resolved', 'resolved_at', 'resolved_by'])
    return redirect('alerts')
