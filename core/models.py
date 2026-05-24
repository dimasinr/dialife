from django.conf import settings
from django.db import models
from django.utils import timezone


class PatientStatus(models.TextChoices):
    STABLE = 'stable', 'Stable'
    WARNING = 'warning', 'Warning'
    CRITICAL = 'critical', 'Critical'
    PENDING = 'pending', 'Pending'


class AlertSeverity(models.TextChoices):
    CRITICAL = 'critical', 'Critical'
    WARNING = 'warning', 'Warning'
    INFO = 'info', 'Information'


class FluidCategory(models.TextChoices):
    DRINK = 'drink', 'Drink'
    FOOD = 'food', 'Food'
    URINE = 'urine', 'Urine'
    OTHER = 'other', 'Other'


class NurseProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nurse_profile',
    )
    employee_id = models.CharField(max_length=32, unique=True)
    ward = models.CharField(max_length=64, default='Ward 4B')
    title = models.CharField(max_length=64, default='Charge Nurse')
    avatar_url = models.URLField(blank=True)

    class Meta:
        ordering = ['employee_id']

    def __str__(self):
        return f'{self.employee_id} — {self.user.get_full_name() or self.user.username}'


class Patient(models.Model):
    patient_code = models.CharField(max_length=32, unique=True)
    full_name = models.CharField(max_length=128)
    age = models.PositiveSmallIntegerField()
    bed = models.CharField(max_length=16, blank=True)
    ward = models.CharField(max_length=64, default='Ward A')
    blood_type = models.CharField(max_length=8, blank=True)
    diagnosis = models.CharField(max_length=128, blank=True)
    dry_weight_kg = models.DecimalField(max_digits=5, decimal_places=1, default=70)
    daily_fluid_limit_ml = models.PositiveIntegerField(default=1000)
    fluid_intake_today_ml = models.PositiveIntegerField(default=0)
    urine_output_24h_ml = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=16,
        choices=PatientStatus.choices,
        default=PatientStatus.STABLE,
    )
    photo_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    admitted_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    @property
    def fluid_percent(self):
        if not self.daily_fluid_limit_ml:
            return 0
        return round((self.fluid_intake_today_ml / self.daily_fluid_limit_ml) * 100)

    @property
    def fluid_over_limit(self):
        return self.fluid_intake_today_ml > self.daily_fluid_limit_ml

    def refresh_status(self):
        pct = self.fluid_percent
        if pct >= 100:
            self.status = PatientStatus.CRITICAL
        elif pct >= 85:
            self.status = PatientStatus.WARNING
        elif self.status == PatientStatus.PENDING:
            pass
        else:
            self.status = PatientStatus.STABLE
        self.save(update_fields=['status', 'updated_at'])


class VitalReading(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='vitals',
    )
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1)
    urine_ml_24h = models.PositiveIntegerField(default=0)
    temperature_c = models.DecimalField(max_digits=4, decimal_places=1, default=36.6)
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f'{self.patient} @ {self.recorded_at:%Y-%m-%d %H:%M}'


class FluidLog(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='fluid_logs',
    )
    category = models.CharField(max_length=16, choices=FluidCategory.choices)
    description = models.CharField(max_length=255)
    volume_ml = models.PositiveIntegerField()
    logged_at = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=16, default='mobile')

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f'{self.patient} — {self.volume_ml}ml'


class Alert(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True,
    )
    severity = models.CharField(max_length=16, choices=AlertSeverity.choices)
    title = models.CharField(max_length=128)
    message = models.TextField()
    equipment_ref = models.CharField(max_length=64, blank=True)
    location = models.CharField(max_length=64, blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts',
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
