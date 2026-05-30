from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import (
    Alert,
    AlertSeverity,
    EducationModule,
    FluidCategory,
    FluidLog,
    FoodItem,
    HDNutritionStatus,
    NurseProfile,
    Patient,
    PatientStatus,
    UserProfile,
    UserRole,
    VitalReading,
)
from core.services.fluid_service import calculate_fluid_limit_ml


class Command(BaseCommand):
    help = 'Seed demo data for DIALIFE monitoring'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username='DI-000001',
            defaults={
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'email': 'sarah.jenkins@dialife.local',
            },
        )
        if created:
            user.set_password('nurse123')
            user.save()
        else:
            user.set_password('nurse123')
            user.save(update_fields=['password'])

        UserProfile.objects.update_or_create(
            user=user,
            defaults={'role': UserRole.NURSE},
        )
        NurseProfile.objects.update_or_create(
            user=user,
            defaults={
                'employee_id': 'DI-000001',
                'ward': 'Ward 4B',
                'title': 'Charge Nurse',
                'avatar_url': (
                    'https://lh3.googleusercontent.com/aida-public/'
                    'AB6AXuAhOWMGocd-U_nJu6l42zCTQ0BWRD5qDBKoH2Od4oWS7vUzrk6AybOvuOh_948rhWWiDl0oJUHG_HbXfv4NiRar5Ys9hGo0N94DfnMzhqNBmoxA5NWuARRbkLBsR4Ds-a6BC86SHQYUnKKDdG_I-9SvAdJUuM7XPJYxY8AEB6OOptLl9kZlto_71hEBOkOPXB4TXUGG2kmWCqpqCoxyaa5TYj9ykFvDzfxCxcXYXVE5pcsxBWHALc5TN-syjN4STkz0LcSeW3JwhG2N'
                ),
            },
        )

        now = timezone.now()

        # Mobile patient account (PRD)
        mobile_email = 'budi.santoso@dialife.local'
        mobile_user, m_created = User.objects.get_or_create(
            username=mobile_email,
            defaults={
                'email': mobile_email,
                'first_name': 'Budi',
                'last_name': 'Santoso',
            },
        )
        mobile_user.set_password('patient123')
        mobile_user.save()
        UserProfile.objects.update_or_create(
            user=mobile_user,
            defaults={'role': UserRole.PATIENT},
        )
        urine_ml = 700
        budi, _ = Patient.objects.update_or_create(
            patient_code='P-99201',
            defaults={
                'user': mobile_user,
                'full_name': 'Budi Santoso',
                'age': 64,
                'bed': '12-A',
                'ward': 'Ward A',
                'blood_type': 'AB+',
                'diagnosis': 'CKD Stage 5',
                'dry_weight_kg': 68.5,
                'daily_fluid_limit_ml': calculate_fluid_limit_ml(urine_ml),
                'urine_output_24h_ml': urine_ml,
                'status': PatientStatus.WARNING,
            },
        )
        budi.sync_fluid_intake_today()

        foods = [
            {
                'name': 'Pisang Ambon',
                'image_name': 'banana.jpg',
                'potassium': 435,
                'phosphorus': 22,
                'sodium': 1,
                'calories': 105,
                'protein': 1.3,
                'estimated_fluid_ml': 80,
                'hd_status': HDNutritionStatus.HINDARI,
                'description': 'Sangat tinggi kalium',
            },
            {
                'name': 'Bakso',
                'image_name': 'bakso.jpg',
                'potassium': 420,
                'phosphorus': 180,
                'sodium': 650,
                'calories': 320,
                'protein': 18,
                'estimated_fluid_ml': 250,
                'hd_status': HDNutritionStatus.BATASI,
                'description': 'Tinggi sodium — batasi porsi',
            },
            {
                'name': 'Nasi Putih',
                'image_name': 'rice.jpg',
                'potassium': 35,
                'phosphorus': 33,
                'sodium': 2,
                'calories': 204,
                'protein': 4,
                'estimated_fluid_ml': 150,
                'hd_status': HDNutritionStatus.AMAN,
                'description': 'Aman dalam porsi terkontrol',
            },
            {
                'name': 'Air Putih',
                'image_name': 'water.jpg',
                'potassium': 0,
                'phosphorus': 0,
                'sodium': 0,
                'calories': 0,
                'protein': 0,
                'estimated_fluid_ml': 200,
                'hd_status': HDNutritionStatus.AMAN,
                'description': 'Hitung dalam batas cairan harian',
            },
        ]
        for f in foods:
            FoodItem.objects.update_or_create(name=f['name'], defaults=f)

        modules = [
            {
                'title': 'Apa itu Hemodialisis',
                'thumbnail_name': 'hd.jpg',
                'content': 'Hemodialisis adalah terapi pengganti fungsi ginjal...',
                'sort_order': 1,
            },
            {
                'title': 'Pembatasan Cairan Harian',
                'thumbnail_name': 'fluid.jpg',
                'content': 'Pasien HD perlu membatasi asupan cairan sesuai anjuran dokter...',
                'sort_order': 2,
            },
            {
                'title': 'Diet Hemodialisis',
                'thumbnail_name': 'diet.jpg',
                'content': 'Diet rendah sodium, kalium, dan fosfor sangat penting...',
                'sort_order': 3,
            },
            {
                'title': 'Makanan yang Harus Dihindari',
                'thumbnail_name': 'avoid.jpg',
                'content': 'Hindari makanan tinggi kalium seperti pisang, kelapa, tomat...',
                'sort_order': 4,
            },
        ]
        for m in modules:
            EducationModule.objects.update_or_create(title=m['title'], defaults=m)

        self.stdout.write(self.style.SUCCESS(
            'Demo ready.\n'
            '  Nurse web: DI-000001 / nurse123\n'
            '  Mobile patient: budi.santoso@dialife.local / patient123'
        ))
