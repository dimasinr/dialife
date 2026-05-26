"""Fluid limit calculation and status helpers (PRD §4.1–4.2)."""

from django.db import models
from django.utils import timezone

from core.models import FluidCategory, FluidLog, FoodScanHistory, Patient


def calculate_fluid_limit_ml(urine_output_ml: int, buffer_ml: int = 500) -> int:
    """Daily fluid limit = urine output + 500 ml."""
    return int(urine_output_ml) + buffer_ml


def fluid_status_label(intake_ml: int, limit_ml: int) -> str:
    """PRD status: aman | waspada | melebihi batas."""
    if limit_ml <= 0:
        return 'aman'
    pct = (intake_ml / limit_ml) * 100
    if pct >= 100:
        return 'melebihi batas'
    if pct >= 85:
        return 'waspada'
    return 'aman'


def fluid_status_from_calculator(urine_output_ml: int, dry_weight: float | None = None) -> str:
    """Status after calculator — informational only."""
    limit = calculate_fluid_limit_ml(urine_output_ml)
    if limit < 1000:
        return 'waspada'
    return 'aman'


def today_intake_ml(patient: Patient) -> int:
    today = timezone.localdate()
    log_sum = (
        FluidLog.objects.filter(
            patient=patient,
            logged_at__date=today,
            category__in=[FluidCategory.DRINK, FluidCategory.FOOD],
        ).aggregate(total=models.Sum('volume_ml'))['total']
        or 0
    )
    scan_sum = (
        FoodScanHistory.objects.filter(
            patient=patient,
            created_at__date=today,
        ).aggregate(total=models.Sum('estimated_fluid_ml'))['total']
        or 0
    )
    return int(log_sum + scan_sum)


def today_food_ml(patient: Patient) -> int:
    today = timezone.localdate()
    return int(
        FluidLog.objects.filter(
            patient=patient,
            logged_at__date=today,
            category=FluidCategory.FOOD,
        ).aggregate(total=models.Sum('volume_ml'))['total']
        or 0
    )


def today_drink_ml(patient: Patient) -> int:
    today = timezone.localdate()
    drink_logs = (
        FluidLog.objects.filter(
            patient=patient,
            logged_at__date=today,
            category=FluidCategory.DRINK,
        ).aggregate(total=models.Sum('volume_ml'))['total']
        or 0
    )
    drink_scans = (
        FoodScanHistory.objects.filter(
            patient=patient,
            created_at__date=today,
            scan_type='drink',
        ).aggregate(total=models.Sum('estimated_fluid_ml'))['total']
        or 0
    )
    return int(drink_logs + drink_scans)
