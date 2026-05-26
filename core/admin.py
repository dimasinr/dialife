from django.contrib import admin

from .models import (
    Alert,
    EducationModule,
    FluidLog,
    FoodItem,
    FoodScanHistory,
    NurseProfile,
    Patient,
    UrineScanHistory,
    UserProfile,
    VitalReading,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)


@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'ward', 'title')
    search_fields = ('employee_id', 'user__username', 'user__first_name')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'patient_code',
        'full_name',
        'user',
        'ward',
        'status',
        'daily_fluid_limit_ml',
        'fluid_intake_today_ml',
    )
    list_filter = ('status', 'ward', 'is_active')
    search_fields = ('patient_code', 'full_name', 'bed')


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'hd_status', 'sodium', 'potassium', 'estimated_fluid_ml', 'is_active')
    list_filter = ('hd_status', 'is_active')
    search_fields = ('name',)


@admin.register(FoodScanHistory)
class FoodScanHistoryAdmin(admin.ModelAdmin):
    list_display = ('patient', 'food_name', 'scan_type', 'estimated_fluid_ml', 'created_at')
    list_filter = ('scan_type', 'hd_status')


@admin.register(UrineScanHistory)
class UrineScanHistoryAdmin(admin.ModelAdmin):
    list_display = ('patient', 'volume_ml', 'confidence', 'created_at')


@admin.register(EducationModule)
class EducationModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'sort_order', 'is_published')
    list_filter = ('is_published',)


@admin.register(VitalReading)
class VitalReadingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'weight_kg', 'urine_ml_24h', 'temperature_c', 'recorded_at')


@admin.register(FluidLog)
class FluidLogAdmin(admin.ModelAdmin):
    list_display = ('patient', 'category', 'volume_ml', 'logged_at', 'source')
    list_filter = ('category', 'source')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'severity', 'patient', 'is_resolved', 'created_at')
    list_filter = ('severity', 'is_resolved')
