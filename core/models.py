from django.conf import settings
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    PATIENT = 'patient', 'Patient'
    NURSE = 'nurse', 'Nurse'


class HDNutritionStatus(models.TextChoices):
    AMAN = 'aman', 'Aman'
    BATASI = 'batasi', 'Batasi'
    HINDARI = 'hindari', 'Hindari'


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


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(
        max_length=16,
        choices=UserRole.choices,
        default=UserRole.PATIENT,
    )
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.user_id} ({self.role})'


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
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_record',
        null=True,
        blank=True,
    )
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

    def sync_fluid_intake_today(self):
        from core.services.fluid_service import today_intake_ml
        self.fluid_intake_today_ml = today_intake_ml(self)
        self.refresh_status()


class FoodItem(models.Model):
    name = models.CharField(max_length=128)
    image = models.ImageField(upload_to='nutrition/', blank=True)
    image_name = models.CharField(max_length=128, blank=True, help_text='Static filename for mobile, e.g. banana.jpg')
    calories = models.PositiveIntegerField(default=0)
    protein = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    sodium = models.PositiveIntegerField(default=0)
    potassium = models.PositiveIntegerField(default=0)
    phosphorus = models.PositiveIntegerField(default=0)
    estimated_fluid_ml = models.PositiveIntegerField(default=0)
    hd_status = models.CharField(
        max_length=16,
        choices=HDNutritionStatus.choices,
        default=HDNutritionStatus.AMAN,
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return self.image_name or ''


class FoodScanHistory(models.Model):
    SCAN_FOOD = 'food'
    SCAN_DRINK = 'drink'
    SCAN_TYPE_CHOICES = [
        (SCAN_FOOD, 'Food'),
        (SCAN_DRINK, 'Drink'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='food_scans',
    )
    food_name = models.CharField(max_length=128)
    scan_type = models.CharField(max_length=16, choices=SCAN_TYPE_CHOICES, default=SCAN_FOOD)
    estimated_fluid_ml = models.PositiveIntegerField(default=0)
    confidence = models.FloatField(default=0.0)
    nutrition_data = models.JSONField(default=dict, blank=True)
    hd_status = models.CharField(
        max_length=16,
        choices=HDNutritionStatus.choices,
        default=HDNutritionStatus.AMAN,
    )
    image = models.ImageField(upload_to='scans/food/', blank=True)
    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Food scan histories'


class UrineScanHistory(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='urine_scans',
    )
    volume_ml = models.PositiveIntegerField()
    confidence = models.FloatField(default=0.0)
    image = models.ImageField(upload_to='scans/urine/', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Urine scan histories'


class EducationModule(models.Model):
    title = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to='education/', blank=True)
    thumbnail_name = models.CharField(max_length=128, blank=True)
    content = models.TextField()
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['sort_order', 'title']

    def __str__(self):
        return self.title

    @property
    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return self.thumbnail_name or ''


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
