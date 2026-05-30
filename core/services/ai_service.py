import os
from .scan_urine_yolo import (
    BASE_DIR,
    _find_best_model,
    _load_class_mapping,
    _get_model,
    predict_volume_from_bytes,
    _model_cache,
)
from .scan_food import predict_food_from_bytes

# Thresholds untuk mengenali gambar
URINE_CONFIDENCE_THRESHOLD = 0.4
FOOD_CONFIDENCE_THRESHOLD = 0.5

# Konfigurasi Path Model — model_ai/urine/best.pt berada di dalam direktori core/
# BASE_DIR = .../core/services/, jadi naik dua level ke core/
_CORE_DIR = os.path.dirname(BASE_DIR)
MODEL_PATH = os.path.join(_CORE_DIR, "model_ai", "urine", "best.pt")

def get_urine_status():
    """Cek status ketersediaan model YOLO."""
    model_path = _find_best_model() or MODEL_PATH
    exists = os.path.isfile(model_path)
    
    status = {
        "model_ready": False,
        "model_file_exists": exists,
        "model_path": model_path,
        "message": ""
    }

    if not exists:
        status["message"] = f"Model tidak ditemukan di {model_path}. Lakukan training terlebih dahulu."
        return status

    try:
        # Test load model
        _get_model(model_path)
        status["model_ready"] = True
        status["message"] = "Model siap digunakan"
        status["model_file_size_mb"] = round(os.path.getsize(model_path) / (1024 * 1024), 2)
    except Exception as e:
        status["message"] = f"Gagal memuat model: {str(e)}"
        status["load_error"] = str(e)

    return status

def get_urine_classes():
    """Format kelas dari mapping JSON ke list untuk frontend UI."""
    mapping = _load_class_mapping()
    classes = []
    for k in sorted(mapping.keys(), key=lambda x: int(x)):
        cls = mapping[k]
        classes.append({
            "id": k,
            "folder_name": cls.get("folder_name", ""),
            "display_name": cls.get("display_name", ""),
            "estimated_ml": cls.get("estimated_ml", 0)
        })
    return classes

def reload_urine_model():
    """Clear YOLO model cache to force reload."""
    _model_cache.clear()

def process_urine_image(image_bytes: bytes, model_path: str):
    """Proses gambar urine dan tambahkan flag is_recognized."""
    result = predict_volume_from_bytes(image_bytes, model_path=model_path)
    result["is_recognized"] = bool(result["confidence"] >= URINE_CONFIDENCE_THRESHOLD)
    return result

def process_food_image(image_bytes: bytes):
    """Proses gambar makanan dan tambahkan flag is_recognized."""
    result = predict_food_from_bytes(image_bytes)
    result["is_recognized"] = bool(result["confidence"] >= FOOD_CONFIDENCE_THRESHOLD)
    return result
