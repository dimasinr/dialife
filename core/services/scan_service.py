"""AI scan MVP — food/drink classification & urine volume estimation (PRD §4.3, §5)."""

import random

from django.core.files.uploadedfile import UploadedFile
from PIL import Image

from core.models import FoodItem, HDNutritionStatus

ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/jpg'}
MAX_IMAGE_BYTES = 5 * 1024 * 1024

# Fallback catalog when DB lookup misses (MVP)
_DEFAULT_FOODS = [
  {
    'name': 'Bakso',
    'calories': 320,
    'protein': 18,
    'sodium': 650,
    'potassium': 420,
    'phosphorus': 180,
    'estimated_fluid_ml': 250,
    'hd_status': HDNutritionStatus.BATASI,
    'scan_type': 'food',
  },
  {
    'name': 'Air Putih',
    'calories': 0,
    'protein': 0,
    'sodium': 0,
    'potassium': 0,
    'phosphorus': 0,
    'estimated_fluid_ml': 200,
    'hd_status': HDNutritionStatus.AMAN,
    'scan_type': 'drink',
  },
  {
    'name': 'Nasi Putih',
    'calories': 204,
    'protein': 4,
    'sodium': 2,
    'potassium': 35,
    'phosphorus': 33,
    'estimated_fluid_ml': 150,
    'hd_status': HDNutritionStatus.AMAN,
    'scan_type': 'food',
  },
]


def validate_upload(image: UploadedFile) -> None:
    if image.size > MAX_IMAGE_BYTES:
        raise ValueError('Image exceeds 5MB limit.')
    content_type = getattr(image, 'content_type', '') or ''
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError('Invalid image type. Use JPEG, PNG, or WebP.')
    try:
        img = Image.open(image)
        img.verify()
        image.seek(0)
    except Exception as exc:
        raise ValueError('Invalid or corrupted image file.') from exc


def _pick_food_item() -> dict:
    items = list(FoodItem.objects.filter(is_active=True).order_by('?')[:5])
    if items:
        item = random.choice(items)
        return {
            'name': item.name,
            'calories': item.calories,
            'protein': float(item.protein),
            'sodium': item.sodium,
            'potassium': item.potassium,
            'phosphorus': item.phosphorus,
            'estimated_fluid_ml': item.estimated_fluid_ml,
            'hd_status': item.hd_status,
            'scan_type': 'drink' if item.estimated_fluid_ml >= 150 and item.sodium < 50 else 'food',
            'food_item': item,
        }
    return {**random.choice(_DEFAULT_FOODS), 'food_item': None}


def scan_food_drink(image: UploadedFile) -> dict:
    """
    MVP: validate image, pick nutrition from DB or fallback catalog.
    Production: replace with MobileNetV2 + CSV lookup.
    """
    validate_upload(image)
    picked = _pick_food_item()
    confidence = round(random.uniform(0.85, 0.97), 2)
    nutrition = {
        'calories': picked['calories'],
        'protein': picked['protein'],
        'sodium': picked['sodium'],
        'potassium': picked['potassium'],
    }
    if picked.get('phosphorus') is not None:
        nutrition['phosphorus'] = picked['phosphorus']
    return {
        'prediction': picked['name'],
        'confidence': confidence,
        'nutrition': nutrition,
        'estimated_fluid_ml': picked['estimated_fluid_ml'],
        'hd_status': picked['hd_status'],
        'scan_type': picked['scan_type'],
        'food_item': picked.get('food_item'),
    }


def scan_urine_volume(image: UploadedFile) -> dict:
    """
    MVP: heuristic from image dimensions; production uses CNN + OpenCV level.
    """
    validate_upload(image)
    try:
        img = Image.open(image)
        w, h = img.size
        image.seek(0)
        # Rough heuristic: larger images → higher estimated fill level
        ratio = min(1.0, (w * h) / (800 * 600))
        base = 300 + int(ratio * 500)
        volume = base + random.randint(-50, 80)
    except Exception:
        volume = random.randint(400, 750)
    volume = max(100, min(volume, 2000))
    return {
        'estimated_volume_ml': volume,
        'confidence': round(random.uniform(0.88, 0.96), 2),
    }
