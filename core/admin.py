from django.contrib import admin

from .models import Alert, FluidLog, NurseProfile, Patient, VitalReading


@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'ward', 'title')
    search_fields = ('employee_id', 'user__username', 'user__first_name')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'patient_code',
        'full_name',
        'ward',
        'bed',
        'status',
        'fluid_intake_today_ml',
        'daily_fluid_limit_ml',
    )
    list_filter = ('status', 'ward', 'is_active')
    search_fields = ('patient_code', 'full_name', 'bed')


@admin.register(VitalReading)
class VitalReadingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'weight_kg', 'urine_ml_24h', 'temperature_c', 'recorded_at')
    list_filter = ('recorded_at',)


@admin.register(FluidLog)
class FluidLogAdmin(admin.ModelAdmin):
    list_display = ('patient', 'category', 'volume_ml', 'logged_at', 'source')
    list_filter = ('category', 'source')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'severity', 'patient', 'is_resolved', 'created_at')
    list_filter = ('severity', 'is_resolved')
