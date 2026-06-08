"""Fluid limit calculation and status helpers (PRD §4.1–4.2)."""

from django.db import models
from django.utils import timezone

from core.models import FluidCategory, FluidLog, Patient


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
    """Calculate the net fluid intake chronologically.

    Food, drink, and other categories add to the running intake, while urine
    output reduces it (without letting the running intake go below 0).
    """
    today = timezone.localdate()
    logs = FluidLog.objects.filter(
        patient=patient,
        logged_at__date=today,
    ).order_by('logged_at')

    running_intake = 0
    for log in logs:
        if log.category in [FluidCategory.DRINK, FluidCategory.FOOD, FluidCategory.OTHER]:
            running_intake += log.volume_ml
        elif log.category == FluidCategory.URINE:
            running_intake = max(0, running_intake - log.volume_ml)

    return running_intake


def today_urine_ml(patient: Patient) -> int:
    """Sum of urine FluidLog entries for today (accumulated output)."""
    today = timezone.localdate()
    return int(
        FluidLog.objects.filter(
            patient=patient,
            logged_at__date=today,
            category=FluidCategory.URINE,
        ).aggregate(total=models.Sum('volume_ml'))['total']
        or 0
    )


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
    """Sum of drink FluidLog entries for today.

    Note: scans already create FluidLog entries, so no need to query
    FoodScanHistory separately.
    """
    today = timezone.localdate()
    return int(
        FluidLog.objects.filter(
            patient=patient,
            logged_at__date=today,
            category=FluidCategory.DRINK,
        ).aggregate(total=models.Sum('volume_ml'))['total']
        or 0
    )
