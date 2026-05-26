from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import EducationModule, FoodItem, Patient, UserProfile, UserRole
from .services.fluid_service import calculate_fluid_limit_ml, fluid_status_from_calculator


class PatientRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    dry_weight = serializers.DecimalField(max_digits=5, decimal_places=1, required=False)
    urine_output_ml = serializers.IntegerField(required=False, default=0, min_value=0)

    def validate_email(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value.lower()

    def create(self, validated_data):
        name = validated_data['name'].strip()
        parts = name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        email = validated_data['email']
        urine = validated_data.get('urine_output_ml', 0)
        dry_weight = validated_data.get('dry_weight', 70)
        limit = calculate_fluid_limit_ml(urine)

        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
        )
        UserProfile.objects.create(user=user, role=UserRole.PATIENT)
        code = f'P-{user.id:05d}'
        patient = Patient.objects.create(
            user=user,
            patient_code=code,
            full_name=name,
            age=0,
            dry_weight_kg=dry_weight,
            daily_fluid_limit_ml=limit,
            urine_output_24h_ml=urine,
        )
        return user, patient


class PatientLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs['email'].lower()
        user = authenticate(username=email, password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not hasattr(user, 'patient_record'):
            raise serializers.ValidationError('Not a patient account.')
        attrs['user'] = user
        return attrs


class FluidCalculateSerializer(serializers.Serializer):
    dry_weight = serializers.DecimalField(max_digits=5, decimal_places=1)
    urine_output_ml = serializers.IntegerField(min_value=0)

    def validate(self, attrs):
        limit = calculate_fluid_limit_ml(attrs['urine_output_ml'])
        attrs['recommended_fluid_limit_ml'] = limit
        attrs['status'] = fluid_status_from_calculator(
            attrs['urine_output_ml'],
            float(attrs['dry_weight']),
        )
        return attrs


class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='user.id')
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email')
    dry_weight = serializers.DecimalField(
        source='dry_weight_kg',
        max_digits=5,
        decimal_places=1,
    )
    fluid_limit_ml = serializers.IntegerField(source='daily_fluid_limit_ml')
    urine_output_ml = serializers.IntegerField()
    patient_id = serializers.IntegerField(source='id')

    def get_name(self, obj):
        return obj.full_name


class ProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    dry_weight = serializers.DecimalField(
        max_digits=5,
        decimal_places=1,
        required=False,
    )
    urine_output_ml = serializers.IntegerField(required=False, min_value=0)
    fluid_limit_ml = serializers.IntegerField(required=False, min_value=0)

    def update_patient(self, patient, validated_data):
        if 'name' in validated_data:
            patient.full_name = validated_data['name']
            parts = validated_data['name'].split(' ', 1)
            patient.user.first_name = parts[0]
            patient.user.last_name = parts[1] if len(parts) > 1 else ''
            patient.user.save(update_fields=['first_name', 'last_name'])
        if 'dry_weight' in validated_data:
            patient.dry_weight_kg = validated_data['dry_weight']
        if 'urine_output_ml' in validated_data:
            patient.urine_output_24h_ml = validated_data['urine_output_ml']
        if 'fluid_limit_ml' in validated_data:
            patient.daily_fluid_limit_ml = validated_data['fluid_limit_ml']
        elif 'urine_output_ml' in validated_data:
            patient.daily_fluid_limit_ml = calculate_fluid_limit_ml(
                validated_data['urine_output_ml'],
            )
        patient.save()
        return patient


class FoodItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = FoodItem
        fields = (
            'id',
            'name',
            'image',
            'potassium',
            'phosphorus',
            'sodium',
            'status',
            'description',
        )

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return obj.image_name or ''


class EducationModuleSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = EducationModule
        fields = ('title', 'thumbnail', 'content')

    def get_thumbnail(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return obj.thumbnail_name or ''
