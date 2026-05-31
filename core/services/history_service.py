"""Aggregate today / history activities for mobile (PRD §4.6)."""

from django.utils import timezone

from core.models import FluidCategory, FluidLog, FoodScanHistory, UrineScanHistory


def _format_time(dt) -> str:
    return timezone.localtime(dt).strftime('%H:%M')


def build_history_entries(patient, date=None, limit=50) -> list[dict]:
    target_date = date or timezone.localdate()
    entries = []

    for scan in FoodScanHistory.objects.filter(
        patient=patient,
        created_at__date=target_date,
    ):
        item = {
            'type': scan.scan_type,
            'name': scan.food_name,
            'time': _format_time(scan.created_at),
        }
        if scan.scan_type == 'food':
            item['estimated_fluid'] = f'{scan.estimated_fluid_ml}ml'
        else:
            item['amount'] = f'{scan.estimated_fluid_ml}ml'
        entries.append((scan.created_at, item))

    for log in FluidLog.objects.filter(patient=patient, logged_at__date=target_date).exclude(source='scan'):
        item = {
            'type': log.category,
            'name': log.description,
            'time': _format_time(log.logged_at),
        }
        if log.category == FluidCategory.FOOD:
            item['estimated_fluid'] = f'{log.volume_ml}ml'
        else:
            item['amount'] = f'{log.volume_ml}ml'
        entries.append((log.logged_at, item))

    for urine in UrineScanHistory.objects.filter(
        patient=patient,
        created_at__date=target_date,
    ):
        entries.append((
            urine.created_at,
            {
                'type': 'urine',
                'name': 'Urine Scan',
                'amount': f'{urine.volume_ml}ml',
                'time': _format_time(urine.created_at),
            },
        ))

    entries.sort(key=lambda x: x[0], reverse=True)
    return [e[1] for e in entries[:limit]]
