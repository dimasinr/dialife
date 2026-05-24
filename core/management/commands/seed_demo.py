from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import (
    Alert,
    AlertSeverity,
    FluidCategory,
    FluidLog,
    NurseProfile,
    Patient,
    PatientStatus,
    VitalReading,
)


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

        patients_data = [
            {
                'patient_code': 'P-99201',
                'full_name': 'Budi Santoso',
                'age': 64,
                'bed': '12-A',
                'ward': 'Ward A',
                'blood_type': 'AB+',
                'diagnosis': 'CKD Stage 5',
                'dry_weight_kg': 68.5,
                'daily_fluid_limit_ml': 1000,
                'fluid_intake_today_ml': 750,
                'urine_output_24h_ml': 450,
                'status': PatientStatus.WARNING,
            },
            {
                'patient_code': 'DX-92831',
                'full_name': 'Robert Chen',
                'age': 58,
                'bed': '12-A',
                'ward': 'Ward A',
                'blood_type': 'O+',
                'diagnosis': 'ESRD',
                'dry_weight_kg': 72.4,
                'daily_fluid_limit_ml': 1000,
                'fluid_intake_today_ml': 1250,
                'urine_output_24h_ml': 150,
                'status': PatientStatus.CRITICAL,
            },
            {
                'patient_code': 'DX-88210',
                'full_name': 'Elena Rodriguez',
                'age': 42,
                'bed': '04-C',
                'ward': 'Ward A',
                'dry_weight_kg': 61.8,
                'daily_fluid_limit_ml': 800,
                'fluid_intake_today_ml': 720,
                'urine_output_24h_ml': 450,
                'status': PatientStatus.WARNING,
            },
            {
                'patient_code': '44920',
                'full_name': 'Jameson, Robert',
                'age': 67,
                'bed': '12-A',
                'ward': 'Ward 4B',
                'daily_fluid_limit_ml': 1200,
                'fluid_intake_today_ml': 1420,
                'status': PatientStatus.CRITICAL,
            },
            {
                'patient_code': '44955',
                'full_name': 'Chen, Wei',
                'age': 55,
                'bed': '04-C',
                'ward': 'Ward 4B',
                'daily_fluid_limit_ml': 1000,
                'fluid_intake_today_ml': 850,
                'status': PatientStatus.STABLE,
            },
            {
                'patient_code': '44912',
                'full_name': 'Smith, Elena',
                'age': 48,
                'bed': '08-B',
                'ward': 'Ward 4B',
                'daily_fluid_limit_ml': 1000,
                'fluid_intake_today_ml': 1020,
                'status': PatientStatus.PENDING,
            },
        ]

        now = timezone.now()
        for data in patients_data:
            patient, _ = Patient.objects.update_or_create(
                patient_code=data['patient_code'],
                defaults=data,
            )
            VitalReading.objects.get_or_create(
                patient=patient,
                recorded_at=now,
                defaults={
                    'weight_kg': data.get('dry_weight_kg', 70),
                    'urine_ml_24h': data.get('urine_output_24h_ml', 400),
                    'temperature_c': 36.7,
                },
            )

        budi = Patient.objects.get(patient_code='P-99201')
        FluidLog.objects.all().delete()
        logs = [
            (FluidCategory.DRINK, 'Mineral Water (Glass)', 250, 8, 15),
            (FluidCategory.FOOD, 'Oatmeal with Banana', 150, 9, 30),
            (FluidCategory.URINE, 'Urine Output (Clear)', 300, 11, 0),
            (FluidCategory.DRINK, 'Herbal Tea', 200, 12, 45),
        ]
        for cat, desc, vol, hour, minute in logs:
            FluidLog.objects.create(
                patient=budi,
                category=cat,
                description=desc,
                volume_ml=vol,
                logged_at=now.replace(hour=hour, minute=minute, second=0),
                source='mobile',
            )

        Alert.objects.all().delete()
        robert = Patient.objects.get(patient_code='44920')
        Alert.objects.create(
            patient=robert,
            severity=AlertSeverity.CRITICAL,
            title='Critical: Fluid Drop',
            message='Sudden fluid volume change detected on monitoring cycle.',
        )
        chen = Patient.objects.get(patient_code='44955')
        Alert.objects.create(
            patient=chen,
            severity=AlertSeverity.WARNING,
            title='Incomplete Intake',
            message='Daily fluid intake log incomplete for current shift.',
        )
        elena = Patient.objects.get(patient_code='44912')
        Alert.objects.create(
            patient=elena,
            severity=AlertSeverity.CRITICAL,
            title='High Flow Rate',
            message='Flow rate above safe threshold. Verify pump settings.',
        )
        Alert.objects.create(
            patient=Patient.objects.get(patient_code='DX-92831'),
            severity=AlertSeverity.CRITICAL,
            title='Fluid volume limit exceeded',
            message='Fluid volume limit exceeded by 500ml. Trend: Rising +50ml/hr.',
        )
        Alert.objects.create(
            severity=AlertSeverity.CRITICAL,
            title='Equipment Failure',
            message='Pressure sensor disconnected or hardware fault detected.',
            equipment_ref='Dialysis Machine D-104',
            location='Room 204-B',
        )
        Alert.objects.create(
            patient=Patient.objects.get(patient_code='DX-88210'),
            severity=AlertSeverity.WARNING,
            title='Missed 24h urine report',
            message='Due at 06:00 AM. Requires manual clinical entry.',
            is_resolved=True,
            resolved_at=now - timedelta(hours=2),
            resolved_by=user,
        )

        self.stdout.write(self.style.SUCCESS(
            'Demo data ready. Login: DI-000001 / nurse123'
        ))
