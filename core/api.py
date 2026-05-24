from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Alert, FluidLog, Patient, VitalReading
from .serializer_api import (
    AlertSerializer,
    FluidLogSerializer,
    LoginSerializer,
    PatientSerializer,
    RegisterNurseSerializer,
    VitalReadingSerializer,
)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        profile = getattr(user, 'nurse_profile', None)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'employee_id': profile.employee_id if profile else user.username,
            'full_name': user.get_full_name() or user.username,
            'ward': profile.ward if profile else '',
        })


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterNurseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response(
            {'message': 'Nurse registered', 'token': token.key, 'user_id': user.id},
            status=status.HTTP_201_CREATED,
        )


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.filter(is_active=True)
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get('status')
        ward = self.request.query_params.get('ward')
        q = self.request.query_params.get('q', '').strip()
        if status:
            qs = qs.filter(status=status)
        if ward:
            qs = qs.filter(ward=ward)
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(full_name__icontains=q)
                | Q(patient_code__icontains=q)
                | Q(bed__icontains=q)
            )
        return qs

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        patient = self.get_object()
        vital = patient.vitals.first()
        return Response({
            'patient': PatientSerializer(patient).data,
            'latest_vital': VitalReadingSerializer(vital).data if vital else None,
            'open_alerts': AlertSerializer(
                patient.alerts.filter(is_resolved=False),
                many=True,
            ).data,
        })


class VitalReadingViewSet(viewsets.ModelViewSet):
    queryset = VitalReading.objects.select_related('patient')
    serializer_class = VitalReadingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        return qs


class FluidLogViewSet(viewsets.ModelViewSet):
    queryset = FluidLog.objects.select_related('patient')
    serializer_class = FluidLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        patient_id = self.request.query_params.get('patient')
        category = self.request.query_params.get('category')
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        if category:
            qs = qs.filter(category=category)
        return qs


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related('patient')
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        severity = self.request.query_params.get('severity')
        is_resolved = self.request.query_params.get('is_resolved')
        patient_id = self.request.query_params.get('patient')
        if severity:
            qs = qs.filter(severity=severity)
        if is_resolved in ('0', '1', 'true', 'false'):
            qs = qs.filter(is_resolved=is_resolved in ('1', 'true'))
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        return qs

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save(update_fields=['is_resolved', 'resolved_at', 'resolved_by'])
        return Response(AlertSerializer(alert).data)


class DashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .models import AlertSeverity, PatientStatus

        patients = Patient.objects.filter(is_active=True)
        return Response({
            'total_patients': patients.count(),
            'critical_patients': patients.filter(status=PatientStatus.CRITICAL).count(),
            'active_alerts': Alert.objects.filter(is_resolved=False).count(),
            'critical_alerts': Alert.objects.filter(
                is_resolved=False,
                severity=AlertSeverity.CRITICAL,
            ).count(),
        })
