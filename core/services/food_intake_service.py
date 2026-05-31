"""Manual food/drink intake from FoodItem catalog (multi-select)."""

from core.models import FluidCategory, FluidLog, FoodItem, FoodScanHistory
from core.services.fluid_service import fluid_status_label, today_intake_ml
from core.services.scan_service import _determine_scan_type


def _nutrition_from_food_item(food: FoodItem) -> dict:
    return {
        'calories': food.calories,
        'protein': float(food.protein),
        'sodium': food.sodium,
        'potassium': food.potassium,
        'phosphorus': food.phosphorus,
    }


def record_manual_food_items(patient, items: list[dict]) -> dict:
    """
    Save one batch of manually selected foods.

    Each item: {"food_id": int, "quantity": int (default 1)}
    """
    saved = []
    batch_total_ml = 0

    for entry in items:
        food_id = entry['food_id']
        quantity = entry.get('quantity', 1)
        try:
            food = FoodItem.objects.get(pk=food_id, is_active=True)
        except FoodItem.DoesNotExist:
            raise ValueError(f'Food item {food_id} not found or inactive.')

        fluid_ml = food.estimated_fluid_ml * quantity
        batch_total_ml += fluid_ml
        nutrition = _nutrition_from_food_item(food)
        scan_type = _determine_scan_type(
            food.name,
            fluid_ml,
            food.sodium,
        )

        history = FoodScanHistory.objects.create(
            patient=patient,
            food_name=food.name if quantity == 1 else f'{food.name} x{quantity}',
            scan_type=scan_type,
            estimated_fluid_ml=fluid_ml,
            confidence=1.0,
            nutrition_data=nutrition,
            hd_status=food.hd_status,
            food_item=food,
        )
        FluidLog.objects.create(
            patient=patient,
            category=(
                FluidCategory.DRINK
                if scan_type == FoodScanHistory.SCAN_DRINK
                else FluidCategory.FOOD
            ),
            description=history.food_name,
            volume_ml=fluid_ml,
            source='manual',
        )
        saved.append({
            'food_id': food.id,
            'name': food.name,
            'quantity': quantity,
            'estimated_fluid_ml': fluid_ml,
            'hd_status': food.hd_status,
            'scan_type': scan_type,
            'nutrition': nutrition,
            'history_id': history.id,
        })

    patient.sync_fluid_intake_today()
    intake = today_intake_ml(patient)
    limit = patient.daily_fluid_limit_ml

    return {
        'items': saved,
        'total_estimated_fluid_ml': batch_total_ml,
        'fluid_intake_ml': intake,
        'fluid_limit_ml': limit,
        'remaining_ml': max(0, limit - intake),
        'status': fluid_status_label(intake, limit),
    }
