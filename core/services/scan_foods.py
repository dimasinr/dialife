import os
import io
import pickle
import re
import numpy as np
import pandas as pd
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

# ==========================================
# CONFIG
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BASE_DIR is .../core/services
CORE_DIR = os.path.dirname(BASE_DIR)
MODEL_DIR = os.path.join(CORE_DIR, "model_ai", "indonesian_food")

CSV_PATH = os.path.join(MODEL_DIR, "nutrition_indonesian_food.csv")
PICKLE_PATH = os.path.join(MODEL_DIR, "food_clip_index.pkl")

# HF Token for model download/verification
device = "cuda" if torch.cuda.is_available() else "cpu"

# ==========================================
# CACHE GLOBALS
# ==========================================
_model = None
_processor = None
_embeddings = None
_labels = None
_nutrition_df = None

def _normalize_name(text):
    return re.sub(r"[_\-]", " ", str(text)).strip().lower()

def _load_food_model():
    global _model, _processor, _embeddings, _labels, _nutrition_df
    
    if _model is None:
        print("Memuat CLIP model untuk Makanan...")
        _model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32"
        ).to(device)
        
    if _processor is None:
        _processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32"
        )
        
    if _embeddings is None or _labels is None:
        if os.path.isfile(PICKLE_PATH):
            print(f"Memuat database embedding dari {PICKLE_PATH}...")
            with open(PICKLE_PATH, "rb") as f:
                db = pickle.load(f)
            _embeddings = np.array(db.get("embeddings", []), dtype=np.float32)
            _labels = db.get("labels", [])
            
            # normalize embeddings database
            if _embeddings is not None and len(_embeddings) > 0:
                _embeddings = _embeddings / np.linalg.norm(_embeddings, axis=1, keepdims=True)
                
    if _nutrition_df is None and os.path.isfile(CSV_PATH):
        _nutrition_df = pd.read_csv(CSV_PATH)


def predict_food_from_bytes(image_bytes: bytes) -> dict:
    """
    Memproses bytes gambar dan mengembalikan prediksi makanan beserta nutrisinya menggunakan CLIP.
    """
    _load_food_model()
    
    if _embeddings is None or _labels is None or _nutrition_df is None:
        raise RuntimeError("Database makanan (embeddings/labels/csv) belum tersedia.")
        
    # Proses Gambar
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    inputs = _processor(
        images=image,
        return_tensors="pt"
    ).to(device)
    
    # Ekstrak Embedding (shape: 1 x D)
    with torch.no_grad():
        outputs = _model.vision_model(**inputs)
        image_features = outputs.pooler_output
        
    # Pastikan tensor normalized
    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
    image_features = image_features.cpu().numpy()
    
    # Hitung Cosine Similarity menggunakan dot product (karena kedua embedding sudah normalized)
    similarities = np.dot(_embeddings, image_features[0])
    
    best_idx = np.argmax(similarities)
    best_label = _labels[best_idx]
    confidence = float(similarities[best_idx])
    
    # Ambil Nutrisi
    nutrition_dict = {}
    best_label_norm = _normalize_name(best_label)
    
    temp_df = _nutrition_df.copy()
    temp_df["norm_name"] = temp_df["name"].apply(_normalize_name)
    food_data = temp_df[temp_df["norm_name"] == best_label_norm]
    
    if not food_data.empty:
        # Konversi baris pertama ke dictionary
        row = food_data.iloc[0]
        if "norm_name" in row:
            row = row.drop("norm_name")
        # Ganti NaN dengan None agar valid di JSON
        row = row.replace({np.nan: None})
        nutrition_dict = row.to_dict()
        
    return {
        "food_name": str(best_label),
        "confidence": confidence,
        "nutrition": nutrition_dict
    }
