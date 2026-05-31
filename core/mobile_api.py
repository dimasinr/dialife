"""Mobile API — HD Care PRD (Flutter patient app)."""

from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .models import (
    EducationModule,
    FluidCategory,
    FluidLog,
    FoodItem,
    FoodScanHistory,
    Patient,
    UrineScanHistory,
)
from .mobile_serializers import (
    FluidCalculateSerializer,
    FoodItemSerializer,
    EducationModuleSerializer,
    ManualFoodBatchSerializer,
    PatientLoginSerializer,
    PatientRegisterSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
)
from .services.fluid_service import (
    calculate_fluid_limit_ml,
    fluid_status_label,
    today_drink_ml,
    today_food_ml,
    today_intake_ml,
)
from .services.food_intake_service import record_manual_food_items
from .services.history_service import build_history_entries
from .services.scan_service import scan_food_drink, scan_urine_volume


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }


def _user_payload(user):
    return {
        'id': user.id,
        'name': user.get_full_name() or user.username,
    }


def get_patient(user) -> Patient:
    try:
        return user.patient_record
    except Patient.DoesNotExist:
        raise PermissionDenied('Patient profile not found for this account.')


def resolve_patient(user, patient_id=None) -> Patient:
    patient = get_patient(user)
    if patient_id and int(patient_id) != patient.id:
        raise PermissionDenied('You can only access your own patient record.')
    return patient


class TokenRefreshAPIView(APIView):
    """Accept `refresh` or `refresh_token` in body (PRD §6)."""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('refresh') or request.data.get('refresh_token')
        if not token:
            raise ValidationError({'refresh_token': 'This field is required.'})
        serializer = TokenRefreshSerializer(data={'refresh': token})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response({
            'access_token': data['access'],
            'refresh_token': data.get('refresh', token),
        })


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PatientRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _patient = serializer.create(serializer.validated_data)
        tokens = _tokens_for_user(user)
        return Response(
            {
                **tokens,
                'user': _user_payload(user),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PatientLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({
            **_tokens_for_user(user),
            'user': _user_payload(user),
        })


class LogoutAPIView(APIView):
    def post(self, request):
        refresh = request.data.get('refresh_token')
        if refresh:
            try:
                token = RefreshToken(refresh)
                token.blacklist()
            except Exception:
                pass
        return Response({'message': 'Logged out successfully.'})


class ProfileAPIView(APIView):
    def get(self, request):
        patient = get_patient(request.user)
        return Response(ProfileSerializer(patient).data)


class ProfileUpdateAPIView(APIView):
    def patch(self, request):
        patient = get_patient(request.user)
        serializer = ProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        patient = serializer.update_patient(patient, serializer.validated_data)
        return Response(ProfileSerializer(patient).data)


class DashboardHomeAPIView(APIView):
    def get(self, request):
        patient = get_patient(request.user)
        patient.sync_fluid_intake_today()
        limit = patient.daily_fluid_limit_ml
        intake = today_intake_ml(patient)
        remaining = max(0, limit - intake)
        return Response({
            'patient_name': patient.full_name,
            'fluid_limit_ml': limit,
            'fluid_intake_ml': intake,
            'remaining_ml': remaining,
            'status': fluid_status_label(intake, limit),
            'today_summary': build_history_entries(patient, limit=20),
            'totals': {
                'food_ml': today_food_ml(patient),
                'drink_ml': today_drink_ml(patient),
                'urine_output_ml': patient.urine_output_24h_ml,
            },
        })


class FluidCalculateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FluidCalculateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            'recommended_fluid_limit_ml': serializer.validated_data['recommended_fluid_limit_ml'],
            'status': serializer.validated_data['status'],
        })


class FoodDrinkScanAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        image = request.FILES.get('image')
        if not image:
            raise ValidationError({'image': 'Image file is required.'})
        patient = resolve_patient(request.user, request.data.get('patient_id'))
        try:
            result = scan_food_drink(image)
        except ValueError as exc:
            raise ValidationError({'image': str(exc)}) from exc

        history = FoodScanHistory.objects.create(
            patient=patient,
            food_name=result['prediction'],
            scan_type=result['scan_type'],
            estimated_fluid_ml=result['estimated_fluid_ml'],
            confidence=result['confidence'],
            nutrition_data=result['nutrition'],
            hd_status=result['hd_status'],
            image=image,
            food_item=result.get('food_item'),
        )
        category = (
            FluidCategory.DRINK
            if result['scan_type'] == 'drink'
            else FluidCategory.FOOD
        )
        FluidLog.objects.create(
            patient=patient,
            category=category,
            description=result['prediction'],
            volume_ml=result['estimated_fluid_ml'],
            source='scan',
        )
        patient.sync_fluid_intake_today()

        return Response({
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'nutrition': result['nutrition'],
            'estimated_fluid_ml': result['estimated_fluid_ml'],
            'hd_status': result['hd_status'],
            'scan_type': result['scan_type'],
            'is_recognized': result.get('is_recognized', True),
            'history_id': history.id,
        })


class UrineScanAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        image = request.FILES.get('image')
        if not image:
            raise ValidationError({'image': 'Image file is required.'})
        patient = resolve_patient(request.user, request.data.get('patient_id'))
        try:
            result = scan_urine_volume(image)
        except ValueError as exc:
            raise ValidationError({'image': str(exc)}) from exc

        UrineScanHistory.objects.create(
            patient=patient,
            volume_ml=result['estimated_volume_ml'],
            confidence=result['confidence'],
            image=image,
        )
        patient.urine_output_24h_ml = result['estimated_volume_ml']
        patient.daily_fluid_limit_ml = calculate_fluid_limit_ml(
            result['estimated_volume_ml'],
        )
        patient.save(
            update_fields=['urine_output_24h_ml', 'daily_fluid_limit_ml', 'updated_at'],
        )
        FluidLog.objects.create(
            patient=patient,
            category=FluidCategory.URINE,
            description='Urine scan (AI)',
            volume_ml=result['estimated_volume_ml'],
            source='scan',
        )
        return Response({
            'estimated_volume_ml': result['estimated_volume_ml'],
            'confidence': result['confidence'],
            'display_name': result.get('display_name', ''),
            'class_name': result.get('class_name', ''),
            'min_ml': result.get('min_ml', 0),
            'max_ml': result.get('max_ml', 0),
            'top3': result.get('top3', []),
            'is_recognized': result.get('is_recognized', False),
        })


class NutritionFoodsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = FoodItem.objects.filter(is_active=True)
        q = request.query_params.get('q', '').strip()
        hd_status = request.query_params.get('status', '').strip()
        if q:
            qs = qs.filter(name__icontains=q)
        if hd_status:
            qs = qs.filter(hd_status=hd_status)
        serializer = FoodItemSerializer(
            qs,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)


class EducationModulesAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = EducationModule.objects.filter(is_published=True)
        serializer = EducationModuleSerializer(
            qs,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)


class FluidIntakeAPIView(APIView):
    """Manual fluid intake — quick action Catat cairan."""

    def post(self, request):
        patient = get_patient(request.user)
        category = request.data.get('type', 'drink')
        if category not in ('drink', 'food'):
            raise ValidationError({'type': 'Must be drink or food.'})
        name = request.data.get('name', '').strip() or 'Manual entry'
        try:
            volume_ml = int(request.data.get('volume_ml', 0))
        except (TypeError, ValueError):
            raise ValidationError({'volume_ml': 'Valid integer required.'})
        if volume_ml <= 0:
            raise ValidationError({'volume_ml': 'Must be greater than zero.'})

        log = FluidLog.objects.create(
            patient=patient,
            category=category,
            description=name,
            volume_ml=volume_ml,
            source='mobile',
        )
        patient.sync_fluid_intake_today()
        return Response(
            {
                'type': category,
                'name': name,
                'amount': f'{volume_ml}ml',
                'time': timezone.localtime(log.logged_at).strftime('%H:%M'),
            },
            status=status.HTTP_201_CREATED,
        )


class ManualFoodInputAPIView(APIView):
    """
    Input manual dari daftar FoodItem (multi-select).
    Menghitung cairan seperti scan, tanpa upload gambar.
    """

    def post(self, request):
        patient = get_patient(request.user)
        serializer = ManualFoodBatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = record_manual_food_items(
                patient,
                serializer.validated_data['items'],
            )
        except ValueError as exc:
            raise ValidationError({'items': str(exc)}) from exc
        return Response(result, status=status.HTTP_201_CREATED)


class HistoryAPIView(APIView):
    def get(self, request):
        patient = get_patient(request.user)
        date_str = request.query_params.get('date')
        target_date = timezone.localdate()
        if date_str:
            try:
                from datetime import datetime
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError({'date': 'Use YYYY-MM-DD format.'})
        return Response(build_history_entries(patient, date=target_date))
