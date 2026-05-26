"""Nurse monitoring API (/api/v1/nurse/) — web dashboard integration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import (
    AlertViewSet,
    DashboardStatsAPIView,
    FluidLogViewSet,
    LoginAPIView,
    PatientViewSet,
    RegisterAPIView,
    VitalReadingViewSet,
)

router = DefaultRouter()
router.register('patients', PatientViewSet, basename='nurse-patient')
router.register('vitals', VitalReadingViewSet, basename='nurse-vital')
router.register('fluid-logs', FluidLogViewSet, basename='nurse-fluid-log')
router.register('alerts', AlertViewSet, basename='nurse-alert')

urlpatterns = [
    path('auth/login/', LoginAPIView.as_view(), name='nurse-api-login'),
    path('auth/register/', RegisterAPIView.as_view(), name='nurse-api-register'),
    path('dashboard/stats/', DashboardStatsAPIView.as_view(), name='nurse-dashboard-stats'),
    path('', include(router.urls)),
]
