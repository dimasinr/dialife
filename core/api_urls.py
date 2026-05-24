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
router.register('patients', PatientViewSet, basename='api-patient')
router.register('vitals', VitalReadingViewSet, basename='api-vital')
router.register('fluid-logs', FluidLogViewSet, basename='api-fluid-log')
router.register('alerts', AlertViewSet, basename='api-alert')

urlpatterns = [
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('dashboard/stats/', DashboardStatsAPIView.as_view(), name='api-dashboard-stats'),
    path('', include(router.urls)),
]
