import os
import io
# pyrefly: ignore [missing-import]
import numpy as np
import pandas as pd
# pyrefly: ignore [missing-import]
from PIL import Image
# pyrefly: ignore [missing-import]
from tensorflow.keras.applications import EfficientNetB0
# pyrefly: ignore [missing-import]
from tensorflow.keras.applications.efficientnet import preprocess_input
# pyrefly: ignore [missing-import]
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import Model

# ==========================================
# CONFIG
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "nutrition Makanan dan Minuman Indonesia.csv")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "food_embeddings.npy")
LABELS_PATH = os.path.join(BASE_DIR, "food_labels.npy")

# ==========================================
# CACHE GLOBALS
# ==========================================
_model = None
_embeddings = None
_labels = None
_nutrition_df = None

def _load_food_model():
    global _model, _embeddings, _labels, _nutrition_df
    
    if _model is None:
        print("Memuat model EfficientNetB0 untuk Makanan...")
        base_model = EfficientNetB0(weights='imagenet', include_top=False, pooling='avg')
        _model = Model(inputs=base_model.input, outputs=base_model.output)
        
    if _embeddings is None and os.path.isfile(EMBEDDINGS_PATH):
        _embeddings = np.load(EMBEDDINGS_PATH)
        
    if _labels is None and os.path.isfile(LABELS_PATH):
        _labels = np.load(LABELS_PATH)
        
    if _nutrition_df is None and os.path.isfile(CSV_PATH):
        _nutrition_df = pd.read_csv(CSV_PATH)


def predict_food_from_bytes(image_bytes: bytes) -> dict:
    """
    Memproses bytes gambar dan mengembalikan prediksi makanan beserta nutrisinya.
    """
    _load_food_model()
    
    if _embeddings is None or _labels is None or _nutrition_df is None:
        raise RuntimeError("Database makanan (embeddings/labels/csv) belum tersedia.")
        
    # Proses Gambar
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize((224, 224))
    
    image_arr = img_to_array(image)
    image_arr = np.expand_dims(image_arr, axis=0)
    image_arr = preprocess_input(image_arr)
    
    # Ekstrak Embedding (shape: 1 x D)
    query_embedding = _model.predict(image_arr, verbose=0)
    
    # Hitung Cosine Similarity manual menggunakan numpy (untuk menghindari dependensi sklearn)
    v1 = query_embedding[0]
    v1_norm = np.linalg.norm(v1)
    v2_norms = np.linalg.norm(_embeddings, axis=1)
    dot_products = np.dot(_embeddings, v1)
    similarities = dot_products / (v1_norm * v2_norms)
    
    best_idx = np.argmax(similarities)
    
    best_label = _labels[best_idx]
    confidence = float(similarities[best_idx])
    
    # Ambil Nutrisi
    food_data = _nutrition_df[_nutrition_df["name"] == best_label]
    nutrition_dict = {}
    
    if not food_data.empty:
        # Konversi baris pertama ke dictionary
        row = food_data.iloc[0]
        # Ganti NaN dengan None agar valid di JSON
        row = row.replace({np.nan: None})
        nutrition_dict = row.to_dict()
        
    return {
        "food_name": str(best_label),
        "confidence": confidence,
        "nutrition": nutrition_dict
    }
