"""
Standalone inference script untuk scan volume urine menggunakan YOLO.

Cara pakai:
    python scan_urine_yolo.py foto_botol.jpg
    python scan_urine_yolo.py foto_botol.jpg --model path/to/best.pt
    python scan_urine_yolo.py --batch folder_gambar/

Untuk integrasi API (Flask/FastAPI), gunakan fungsi:
    from scan_urine_yolo import predict_volume, predict_volume_from_bytes
"""

import argparse
import io
import json
import os
import sys
import re
from pathlib import Path

# ==============================================================================
# KONFIGURASI
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLASS_MAPPING_PATH = os.path.join(BASE_DIR, "yolo_class_mapping.json")
RUNS_DIR = os.path.join(BASE_DIR, "runs")
PROJECT_NAME = "urine_volume_cls"
IMAGE_SIZE = 224


def _find_best_model() -> str | None:
    """Cari model terbaik dari hasil training."""
    classify_dir = os.path.join(RUNS_DIR, "classify")
    if not os.path.isdir(classify_dir):
        return None

    candidates = []
    for d in os.listdir(classify_dir):
        if d.startswith(PROJECT_NAME):
            best = os.path.join(classify_dir, d, "weights", "best.pt")
            if os.path.isfile(best):
                candidates.append(best)

    # Juga cek langsung
    direct = os.path.join(classify_dir, PROJECT_NAME, "weights", "best.pt")
    if os.path.isfile(direct) and direct not in candidates:
        candidates.append(direct)

    return sorted(candidates)[-1] if candidates else None


def _load_class_mapping() -> dict:
    """Load class mapping dari JSON."""
    if os.path.isfile(CLASS_MAPPING_PATH):
        with open(CLASS_MAPPING_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _parse_class_name(class_name: str) -> dict:
    """Parse info volume dari nama kelas. E.g. '601_700ml' -> {min: 601, max: 700, est: 650}."""
    match = re.match(r"(\d+)_(\d+)ml", class_name)
    if match:
        min_ml = int(match.group(1))
        max_ml = int(match.group(2))
        return {
            "min_ml": min_ml,
            "max_ml": max_ml,
            "estimated_ml": (min_ml + max_ml) // 2,
            "display": f"{min_ml} - {max_ml} ml",
        }
    return {"min_ml": 0, "max_ml": 0, "estimated_ml": 0, "display": class_name}


# Cache model agar tidak load berulang
_model_cache = {}


def _get_model(model_path: str | None = None):
    """Load atau ambil model dari cache."""
    from ultralytics import YOLO

    if model_path is None:
        model_path = _find_best_model()

    if model_path is None:
        raise RuntimeError(
            "Model tidak ditemukan! Jalankan dulu:\n"
            "  python train_yolo_urine.py --train"
        )

    if model_path not in _model_cache:
        _model_cache[model_path] = YOLO(model_path)

    return _model_cache[model_path], model_path


def predict_volume(image_path: str, model_path: str | None = None) -> dict:
    """
    Prediksi volume urine dari file gambar.

    Args:
        image_path: Path ke file gambar
        model_path: Path ke model .pt (opsional, auto-detect)

    Returns:
        dict dengan keys:
            - class_name: nama kelas (e.g. '601_700ml')
            - display_name: nama tampilan (e.g. '601 - 700 ml')
            - estimated_ml: estimasi ml (e.g. 650)
            - min_ml, max_ml: range volume
            - confidence: confidence score (0-1)
            - top3: list top-3 prediksi
    """
    model, used_path = _get_model(model_path)
    mapping = _load_class_mapping()

    results = model.predict(image_path, imgsz=IMAGE_SIZE, verbose=False)

    if not results:
        raise RuntimeError("Tidak ada hasil prediksi.")

    result = results[0]
    probs = result.probs

    top1_idx = probs.top1
    top1_conf = probs.top1conf.item()
    class_name = result.names[top1_idx]

    # Info volume dari mapping atau parse nama kelas
    if str(top1_idx) in mapping:
        info = mapping[str(top1_idx)]
    else:
        info = _parse_class_name(class_name)

    # Top-3
    top5_indices = probs.top5
    top5_confs = probs.top5conf.tolist()
    top3 = []
    for idx, conf in zip(top5_indices[:3], top5_confs[:3]):
        name = result.names[idx]
        parsed = _parse_class_name(name)
        top3.append({
            "class_name": name,
            "estimated_ml": parsed["estimated_ml"],
            "confidence": round(conf, 4),
        })

    return {
        "class_name": class_name,
        "display_name": info.get("display_name", info.get("display", class_name)),
        "estimated_ml": info.get("estimated_ml", 0),
        "min_ml": info.get("min_ml", 0),
        "max_ml": info.get("max_ml", 0),
        "confidence": round(top1_conf, 4),
        "top3": top3,
    }


def predict_volume_from_bytes(image_bytes: bytes, model_path: str | None = None) -> dict:
    """
    Prediksi volume dari bytes gambar (untuk API endpoint).

    Args:
        image_bytes: bytes gambar (JPEG/PNG)
        model_path: Path ke model .pt (opsional)

    Returns:
        dict sama seperti predict_volume()
    """
    from PIL import Image

    img = Image.open(io.BytesIO(image_bytes))

    # Simpan ke temp file (YOLO butuh path atau numpy array)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        img.save(tmp, format="JPEG")
        tmp_path = tmp.name

    try:
        return predict_volume(tmp_path, model_path)
    finally:
        os.unlink(tmp_path)


def print_result(result: dict, image_path: str):
    """Print hasil prediksi ke console."""
    print()
    print("=" * 50)
    print("   HASIL SCAN VOLUME URINE")
    print("=" * 50)
    print(f"  Gambar       : {os.path.basename(image_path)}")
    print(f"  Kelas        : {result['class_name']}")
    print(f"  Range        : {result['display_name']}")
    print(f"  Estimasi     : ~{result['estimated_ml']} ml")
    print(f"  Confidence   : {result['confidence'] * 100:.1f}%")
    print("-" * 50)
    print("  Top-3 Prediksi:")
    for i, pred in enumerate(result.get("top3", [])):
        print(f"    {i+1}. {pred['class_name']} (~{pred['estimated_ml']} ml) — {pred['confidence'] * 100:.1f}%")
    print("=" * 50)


def batch_predict(folder_path: str, model_path: str | None = None):
    """Prediksi batch dari folder gambar."""
    image_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    images = [
        f for f in Path(folder_path).iterdir()
        if f.suffix.lower() in image_exts
    ]

    if not images:
        print(f"Tidak ada gambar di: {folder_path}")
        return

    print(f"Memproses {len(images)} gambar dari: {folder_path}")
    print()

    results = []
    for img_path in sorted(images):
        try:
            result = predict_volume(str(img_path), model_path)
            results.append({"file": img_path.name, **result})
            print(f"  {img_path.name:30s} → ~{result['estimated_ml']:4d} ml  ({result['confidence']*100:.1f}%)")
        except Exception as e:
            print(f"  {img_path.name:30s} → ERROR: {e}")

    print()
    print(f"Total: {len(results)}/{len(images)} berhasil diprediksi")
    return results


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scan volume urine dari gambar botol menggunakan YOLO"
    )
    parser.add_argument(
        "image",
        nargs="?",
        help="Path ke file gambar (atau folder dengan --batch)",
    )
    parser.add_argument(
        "--model",
        metavar="PATH",
        help="Path ke model .pt",
    )
    parser.add_argument(
        "--batch",
        metavar="FOLDER",
        help="Prediksi semua gambar dalam folder",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output dalam format JSON",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        import ultralytics  # noqa: F401
    except ImportError:
        print("Error: ultralytics belum terinstal!")
        print("Install: pip install ultralytics")
        sys.exit(1)

    if args.batch:
        results = batch_predict(args.batch, model_path=args.model)
        if args.json and results:
            print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.image:
        if not os.path.isfile(args.image):
            print(f"File tidak ditemukan: {args.image}")
            sys.exit(1)

        result = predict_volume(args.image, model_path=args.model)

        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print_result(result, args.image)

    else:
        print("Cara pakai:")
        print("  python scan_urine_yolo.py foto_botol.jpg")
        print("  python scan_urine_yolo.py --batch folder_gambar/")
        print("  python scan_urine_yolo.py foto.jpg --json")
        sys.exit(1)


if __name__ == "__main__":
    main()
