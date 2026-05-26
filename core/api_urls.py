"""Mobile API routes — PRD HD Care (/api/)."""

from django.urls import path
from .mobile_api import (
    DashboardHomeAPIView,
    EducationModulesAPIView,
    FluidCalculateAPIView,
    FluidIntakeAPIView,
    FoodDrinkScanAPIView,
    HistoryAPIView,
    LoginAPIView,
    LogoutAPIView,
    NutritionFoodsAPIView,
    ProfileAPIView,
    ProfileUpdateAPIView,
    RegisterAPIView,
    TokenRefreshAPIView,
    UrineScanAPIView,
)

urlpatterns = [
    # §6 Authentication
    path('auth/register/', RegisterAPIView.as_view(), name='api-auth-register'),
    path('auth/login/', LoginAPIView.as_view(), name='api-auth-login'),
    path('auth/refresh/', TokenRefreshAPIView.as_view(), name='api-auth-refresh'),
    path('logout/', LogoutAPIView.as_view(), name='api-logout'),
    # §4.7 Akun
    path('profile/', ProfileAPIView.as_view(), name='api-profile'),
    path('profile/update/', ProfileUpdateAPIView.as_view(), name='api-profile-update'),
    # §4.1 Beranda
    path('dashboard/home/', DashboardHomeAPIView.as_view(), name='api-dashboard-home'),
    # §4.2 Kalkulator
    path('fluid/calculate/', FluidCalculateAPIView.as_view(), name='api-fluid-calculate'),
    path('fluid/intake/', FluidIntakeAPIView.as_view(), name='api-fluid-intake'),
    # §4.3 Scan
    path('scan/food-drink/', FoodDrinkScanAPIView.as_view(), name='api-scan-food-drink'),
    # §5 Urine scan
    path('scan/urine/', UrineScanAPIView.as_view(), name='api-scan-urine'),
    # §4.4 Nutrisi
    path('nutrition/foods/', NutritionFoodsAPIView.as_view(), name='api-nutrition-foods'),
    # §4.5 Edukasi
    path('education/modules/', EducationModulesAPIView.as_view(), name='api-education-modules'),
    # §4.6 Riwayat
    path('history/', HistoryAPIView.as_view(), name='api-history'),
]
