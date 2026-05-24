from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Alert, FluidLog, NurseProfile, Patient, VitalReading


class NurseProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = NurseProfile
        fields = ('employee_id', 'ward', 'title', 'avatar_url', 'full_name')

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class LoginSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs['employee_id'],
            password=attrs['password'],
        )
        if not user:
            raise serializers.ValidationError('Invalid credentials.')
        attrs['user'] = user
        return attrs


class RegisterNurseSerializer(serializers.Serializer):
    employee_id = serializers.CharField(max_length=32)
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(max_length=64)
    last_name = serializers.CharField(max_length=64, required=False, allow_blank=True)
    ward = serializers.CharField(max_length=64, default='Ward 4B')
    title = serializers.CharField(max_length=64, default='Nurse')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['employee_id'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name', ''),
        )
        NurseProfile.objects.create(
            user=user,
            employee_id=validated_data['employee_id'],
            ward=validated_data['ward'],
            title=validated_data['title'],
        )
        return user


class PatientSerializer(serializers.ModelSerializer):
    fluid_percent = serializers.IntegerField(read_only=True)
    fluid_over_limit = serializers.BooleanField(read_only=True)

    class Meta:
        model = Patient
        fields = (
            'id',
            'patient_code',
            'full_name',
            'age',
            'bed',
            'ward',
            'blood_type',
            'diagnosis',
            'dry_weight_kg',
            'daily_fluid_limit_ml',
            'fluid_intake_today_ml',
            'urine_output_24h_ml',
            'status',
            'photo_url',
            'fluid_percent',
            'fluid_over_limit',
            'is_active',
            'updated_at',
        )
        read_only_fields = ('fluid_intake_today_ml', 'status', 'updated_at')


class VitalReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalReading
        fields = (
            'id',
            'patient',
            'weight_kg',
            'urine_ml_24h',
            'temperature_c',
            'recorded_at',
        )


class FluidLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FluidLog
        fields = (
            'id',
            'patient',
            'category',
            'description',
            'volume_ml',
            'logged_at',
            'source',
        )
        read_only_fields = ('logged_at',)

    def create(self, validated_data):
        log = super().create(validated_data)
        patient = log.patient
        if log.category in ('drink', 'food'):
            patient.fluid_intake_today_ml += log.volume_ml
            patient.save(update_fields=['fluid_intake_today_ml', 'updated_at'])
        elif log.category == 'urine':
            patient.urine_output_24h_ml = log.volume_ml
            patient.save(update_fields=['urine_output_24h_ml', 'updated_at'])
        patient.refresh_status()
        return log


class AlertSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_code = serializers.CharField(source='patient.patient_code', read_only=True)

    class Meta:
        model = Alert
        fields = (
            'id',
            'patient',
            'patient_name',
            'patient_code',
            'severity',
            'title',
            'message',
            'equipment_ref',
            'location',
            'is_resolved',
            'resolved_at',
            'created_at',
        )
        read_only_fields = ('resolved_at', 'created_at')
