"""AI scan — food/drink classification & urine volume estimation (PRD §4.3, §5).

scan_food_drink  → EfficientNetB0 embedding similarity + CSV nutrition lookup
scan_urine_volume → YOLO classification (best.pt di model_ai/urine/)

Panggilan model sudah terintegrasi penuh. Tidak ada lagi fallback/mock data.
"""

import logging

from django.core.files.uploadedfile import UploadedFile
from PIL import Image

from core.models import FoodItem, HDNutritionStatus

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/jpg'}
MAX_IMAGE_BYTES = 5 * 1024 * 1024


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _determine_scan_type(food_name: str, estimated_fluid_ml: int, sodium: int) -> str:
    """Tentukan apakah hasil scan adalah makanan atau minuman."""
    DRINK_KEYWORDS = [
        'air', 'jus', 'juice', 'teh', 'kopi', 'susu', 'milk', 'soda',
        'minuman', 'drink', 'es', 'sirup', 'infus', 'yakult', 'milo',
    ]
    name_lower = food_name.lower()
    if any(kw in name_lower for kw in DRINK_KEYWORDS):
        return 'drink'
    if estimated_fluid_ml >= 150 and sodium < 50:
        return 'drink'
    return 'food'


def _determine_hd_status(sodium: int, potassium: int, phosphorus: int) -> str:
    """
    Tentukan status HD (hemodialysis) berdasarkan nilai nutrisi.
    Nilai ambang batas sesuai panduan diet ginjal umum.
    """
    if sodium > 500 or potassium > 400 or phosphorus > 250:
        return HDNutritionStatus.HINDARI
    if sodium > 200 or potassium > 200 or phosphorus > 120:
        return HDNutritionStatus.BATASI
    return HDNutritionStatus.AMAN


def _nutrition_from_ai_result(ai_nutrition: dict) -> dict:
    """
    Ekstrak field nutrisi relevan dari hasil predict_food_from_bytes()
    dan konversi ke format standar API.
    """
    def _safe_int(val, default=0) -> int:
        try:
            return int(float(val)) if val is not None else default
        except (TypeError, ValueError):
            return default

    def _safe_float(val, default=0.0) -> float:
        try:
            return float(val) if val is not None else default
        except (TypeError, ValueError):
            return default

    return {
        'calories':   _safe_int(ai_nutrition.get('calories') or ai_nutrition.get('Kalori (kcal)')),
        'protein':    _safe_float(ai_nutrition.get('protein') or ai_nutrition.get('Protein (g)')),
        'sodium':     _safe_int(ai_nutrition.get('sodium') or ai_nutrition.get('Natrium (mg)')),
        'potassium':  _safe_int(ai_nutrition.get('potassium') or ai_nutrition.get('Kalium (mg)')),
        'phosphorus': _safe_int(ai_nutrition.get('phosphorus') or ai_nutrition.get('Fosfor (mg)')),
    }


def _estimated_fluid_from_ai(ai_nutrition: dict, food_name: str) -> int:
    """Ambil estimasi cairan dari data CSV, atau gunakan heuristik."""
    # Beberapa CSV memiliki kolom estimasi cairan
    for key in ('estimated_fluid_ml', 'Estimasi Cairan (ml)', 'cairan_ml'):
        if ai_nutrition.get(key) is not None:
            try:
                return int(float(ai_nutrition[key]))
            except (TypeError, ValueError):
                pass
    # Heuristik berdasarkan nama makanan
    name_lower = food_name.lower()
    if any(kw in name_lower for kw in ['air', 'jus', 'teh', 'kopi', 'susu', 'soda', 'minuman']):
        return 200
    if any(kw in name_lower for kw in ['sup', 'soto', 'kuah', 'bakso', 'rawon', 'pho']):
        return 300
    return 100  # makanan padat default


def _lookup_food_item_by_name(name: str):
    """Cari FoodItem di database berdasarkan nama (case-insensitive)."""
    try:
        return FoodItem.objects.filter(
            name__icontains=name, is_active=True
        ).first()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scan_food_drink(image: UploadedFile) -> dict:
    """
    Scan gambar makanan/minuman menggunakan EfficientNetB0 + embedding similarity.

    Alur:
    1. Validasi gambar
    2. Panggil process_food_image() dari ai_service.py
    3. Map hasil AI → format standar API
    4. Cari FoodItem di DB untuk mendapatkan data HD-status yang akurat
    """
    validate_upload(image)
    image_bytes = image.read()
    image.seek(0)

    try:
        from .ai_service import process_food_image, FOOD_CONFIDENCE_THRESHOLD
        ai_result = process_food_image(image_bytes)
    except Exception as exc:
        logger.exception("AI model error during food scan")
        raise ValueError(f"Sistem AI untuk scan makanan sedang tidak tersedia: {exc}")

    food_name   = ai_result.get('food_name', 'Unknown')
    confidence  = float(ai_result.get('confidence', 0.0))
    ai_nutrition = ai_result.get('nutrition', {})
    is_recognized = ai_result.get('is_recognized', confidence >= FOOD_CONFIDENCE_THRESHOLD)

    if not is_recognized:
        logger.info("Food scan: gambar tidak dikenali (conf=%.2f), menggunakan best-guess", confidence)

    nutrition = _nutrition_from_ai_result(ai_nutrition)
    estimated_fluid_ml = _estimated_fluid_from_ai(ai_nutrition, food_name)
    scan_type = _determine_scan_type(food_name, estimated_fluid_ml, nutrition['sodium'])
    hd_status = _determine_hd_status(
        nutrition['sodium'], nutrition['potassium'], nutrition['phosphorus']
    )

    # Coba match dengan FoodItem di DB untuk override hd_status & fluid yang lebih akurat
    food_item = _lookup_food_item_by_name(food_name)
    if food_item:
        hd_status = food_item.hd_status
        estimated_fluid_ml = food_item.estimated_fluid_ml or estimated_fluid_ml
        scan_type = 'drink' if food_item.estimated_fluid_ml >= 150 and food_item.sodium < 50 else 'food'

    return {
        'prediction':        food_name,
        'confidence':        round(confidence, 4),
        'nutrition':         nutrition,
        'estimated_fluid_ml': estimated_fluid_ml,
        'hd_status':         hd_status,
        'scan_type':         scan_type,
        'food_item':         food_item,
        'is_recognized':     is_recognized,
    }


def scan_urine_volume(image: UploadedFile) -> dict:
    """
    Scan gambar botol urine menggunakan YOLO classification.

    Alur:
    1. Validasi gambar
    2. Panggil process_urine_image() dari ai_service.py (model best.pt)
    3. Map hasil YOLO → format standar API
    """
    validate_upload(image)
    image_bytes = image.read()
    image.seek(0)

    try:
        from .ai_service import process_urine_image, MODEL_PATH, _find_best_model
        model_path = _find_best_model() or MODEL_PATH
        ai_result = process_urine_image(image_bytes, model_path=model_path)
    except Exception as exc:
        logger.exception("AI model error during urine scan")
        raise ValueError(f"Sistem AI untuk scan urine sedang tidak tersedia: {exc}")

    return {
        'estimated_volume_ml': ai_result.get('estimated_ml', 0),
        'confidence':          round(float(ai_result.get('confidence', 0.0)), 4),
        'class_name':          ai_result.get('class_name', ''),
        'display_name':        ai_result.get('display_name', ''),
        'min_ml':              ai_result.get('min_ml', 0),
        'max_ml':              ai_result.get('max_ml', 0),
        'top3':                ai_result.get('top3', []),
        'is_recognized':       ai_result.get('is_recognized', False),
    }
