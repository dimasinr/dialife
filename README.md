# DiaLife Mobile API Documentation

> **Base URL:** `http://<host>/api/`  
> **Auth:** JWT Bearer Token — `Authorization: Bearer <access_token>`  
> **Content-Type:** `application/json` (unless noted as `multipart/form-data`)

---

## Table of Contents

1. [Authentication](#1-authentication)
   - [Register](#11-post-apiauthregister)
   - [Login](#12-post-apiauthlogin)
   - [Refresh Token](#13-post-apiauthrefresh)
   - [Logout](#14-post-apilogout)
2. [Profile / Akun](#2-profile--akun)
   - [Get Profile](#21-get-apiprofile)
   - [Update Profile](#22-patch-apiprofileupdate)
3. [Dashboard / Beranda](#3-dashboard--beranda)
   - [Dashboard Home](#31-get-apidashboardhome)
4. [Fluid / Kalkulator Cairan](#4-fluid--kalkulator-cairan)
   - [Calculate Fluid Limit](#41-post-apifluidcalculate)
   - [Log Fluid Intake](#42-post-apifluidintake)
5. [Scan](#5-scan)
   - [Scan Food or Drink](#51-post-apiscanfood-drink)
   - [Scan Urine](#52-post-apiscanurineuria)
6. [Nutrition / Nutrisi](#6-nutrition--nutrisi)
   - [List Foods](#61-get-apinutritionfoods)
7. [Education / Edukasi](#7-education--edukasi)
   - [List Modules](#71-get-apieducationmodules)
8. [History / Riwayat](#8-history--riwayat)
   - [Get History](#81-get-apihistory)
9. [Error Responses](#9-error-responses)

---

## 1. Authentication

### 1.1 `POST /api/auth/register/`

Mendaftarkan akun pasien baru. Tidak membutuhkan autentikasi.

**Request Body**

| Field | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| `name` | `string` | ✅ | Nama lengkap pasien |
| `email` | `string` | ✅ | Alamat email (digunakan sebagai username) |
| `password` | `string` | ✅ | Minimum 6 karakter |
| `dry_weight` | `decimal` | ❌ | Berat kering dalam kg (default: 70) |
| `urine_output_ml` | `integer` | ❌ | Output urine 24 jam dalam ml (default: 0) |

**Request Example**

```json
POST /api/auth/register/
Content-Type: application/json

{
  "name": "Budi Santoso",
  "email": "budi.santoso@dialife.local",
  "password": "patient123",
  "dry_weight": 65.5,
  "urine_output_ml": 400
}
```

**Response — `201 Created`**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 5,
    "name": "Budi Santoso"
  }
}
```

**Error — `400 Bad Request`** (email sudah terdaftar)

```json
{
  "email": ["Email already registered."]
}
```

---

### 1.2 `POST /api/auth/login/`

Login pasien dan mendapatkan JWT token.

**Request Body**

| Field | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| `email` | `string` | ✅ | Email akun |
| `password` | `string` | ✅ | Password akun |

**Request Example**

```json
POST /api/auth/login/
Content-Type: application/json

{
  "email": "budi.santoso@dialife.local",
  "password": "patient123"
}
```

**Response — `200 OK`**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 5,
    "name": "Budi Santoso"
  }
}
```

**Error — `400 Bad Request`**

```json
{
  "non_field_errors": ["Invalid email or password."]
}
```

---

### 1.3 `POST /api/auth/refresh/`

Memperbarui access token menggunakan refresh token.

**Request Body**

| Field | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| `refresh_token` | `string` | ✅* | Refresh token (bisa juga key `refresh`) |

> *Mendukung key `refresh` atau `refresh_token`.

**Request Example**

```json
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response — `200 OK`**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error — `400 Bad Request`**

```json
{
  "refresh_token": ["This field is required."]
}
```

---

### 1.4 `POST /api/logout/`

Logout dan blacklist refresh token. **Membutuhkan autentikasi.**

**Headers**

```
Authorization: Bearer <access_token>
```

**Request Body**

| Field | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| `refresh_token` | `string` | ❌ | Refresh token untuk di-blacklist |

**Request Example**

```json
POST /api/logout/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response — `200 OK`**

```json
{
  "message": "Logged out successfully."
}
```

---

## 2. Profile / Akun

> Semua endpoint di seksi ini **membutuhkan autentikasi**.  
> Header: `Authorization: Bearer <access_token>`

### 2.1 `GET /api/profile/`

Mendapatkan detail profil pasien yang sedang login.

**Request Example**

```
GET /api/profile/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response — `200 OK`**

```json
{
  "id": 5,
  "patient_id": 3,
  "name": "Budi Santoso",
  "email": "budi.santoso@dialife.local",
  "dry_weight": "65.5",
  "fluid_limit_ml": 900,
  "urine_output_ml": 400
}
```

---

### 2.2 `PATCH /api/profile/update/`

Memperbarui profil pasien. Semua field bersifat opsional.

**Request Body**

| Field | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| `name` | `string` | ❌ | Nama lengkap baru |
| `dry_weight` | `decimal` | ❌ | Berat kering baru (kg) |
| `urine_output_ml` | `integer` | ❌ | Output urine 24 jam baru (ml) |
| `fluid_limit_ml` | `integer` | ❌ | Override batas cairan harian (ml) |

> Jika `urine_output_ml` diubah tanpa `fluid_limit_ml`, maka `fluid_limit_ml` dihitung ulang secara otomatis.

**Request Example**

```json
PATCH /api/profile/update/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "dry_weight": 64.0,
  "urine_output_ml": 500
}
```

**Response — `200 OK`**

```json
{
  "id": 5,
  "patient_id": 3,
  "name": "Budi Santoso",
  "email": "budi.santoso@dialife.local",
  "dry_weight": "64.0",
  "fluid_limit_ml": 1000,
  "urine_output_ml": 500
}
```

---

## 3. Dashboard / Beranda

### 3.1 `GET /api/dashboard/home/`

Mendapatkan ringkasan data pasien untuk halaman beranda. **Membutuhkan autentikasi.**

**Request Example**

```
GET /api/dashboard/home/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response — `200 OK`**

```json
{
  "patient_name": "Budi Santoso",
  "fluid_limit_ml": 900,
  "fluid_intake_ml": 350,
  "remaining_ml": 550,
  "status": "Aman",
  "totals": {
    "food_ml": 150,
    "drink_ml": 200,
    "urine_output_ml": 400
  },
  "today_summary": [
    {
      "time": "08:30",
      "type": "drink",
      "name": "Air Putih",
      "amount": "200ml",
      "source": "manual"
    },
    {
      "time": "07:15",
      "type": "food",
      "name": "Nasi Goreng",
      "amount": "150ml",
      "source": "scan"
    }
  ]
}
```

| Field | Description |
| :--- | :--- |
| `fluid_limit_ml` | Batas cairan harian dalam ml |
| `fluid_intake_ml` | Total cairan yang sudah dikonsumsi hari ini |
| `remaining_ml` | Sisa cairan yang diperbolehkan |
| `status` | Status konsumsi cairan (mis. `"Aman"`, `"Mendekati Batas"`, `"Melebihi Batas"`) |
| `today_summary` | Array ringkasan aktivitas cairan hari ini |

---

## 4. Fluid / Kalkulator Cairan

### 4.1 `POST /api/fluid/calculate/`

Menghitung rekomendasi batas cairan harian. Tidak membutuhkan autentikasi.

> **Formula:** `fluid_limit_ml = urine_output_ml + 500`

**Request Body**

| Field | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| `dry_weight` | `decimal` | ✅ | Berat kering pasien (kg) |
| `urine_output_ml` | `integer` | ✅ | Output urine 24 jam (ml, ≥ 0) |

**Request Example**

```json
POST /api/fluid/calculate/
Content-Type: application/json

{
  "dry_weight": 65.5,
  "urine_output_ml": 400
}
```

**Response — `200 OK`**

```json
{
  "recommended_fluid_limit_ml": 900,
  "status": "Oliguria ringan — batasi cairan."
}
```

---

### 4.2 `POST /api/fluid/intake/`

Mencatat konsumsi cairan secara manual. **Membutuhkan autentikasi.**

**Request Body**

| Field | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| `type` | `string` | ✅ | Jenis: `"drink"` atau `"food"` |
| `name` | `string` | ❌ | Nama item (default: `"Manual entry"`) |
| `volume_ml` | `integer` | ✅ | Volume dalam ml (> 0) |

**Request Example**

```json
POST /api/fluid/intake/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "type": "drink",
  "name": "Air Putih",
  "volume_ml": 200
}
```

**Response — `201 Created`**

```json
{
  "type": "drink",
  "name": "Air Putih",
  "amount": "200ml",
  "time": "14:30"
}
```

**Error — `400 Bad Request`**

```json
{
  "type": ["Must be drink or food."]
}
```

---

## 5. Scan

> Semua scan endpoint menggunakan `multipart/form-data` dan **membutuhkan autentikasi**.

### 5.1 `POST /api/scan/food-drink/`

Scan gambar makanan atau minuman menggunakan AI.

**Content-Type:** `multipart/form-data`

**Request Fields**

| Field | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| `image` | `file` | ✅ | File gambar makanan/minuman |
| `patient_id` | `integer` | ❌ | ID pasien (validasi kepemilikan) |

**Request Example**

```
POST /api/scan/food-drink/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data

image=<file_binary>
patient_id=3
```

**Response — `200 OK`**

```json
{
  "prediction": "Nasi Goreng",
  "confidence": 0.92,
  "nutrition": {
    "calories": 250,
    "protein_g": 8.0,
    "carbs_g": 40.0,
    "fat_g": 7.5,
    "potassium_mg": 180,
    "phosphorus_mg": 120,
    "sodium_mg": 550
  },
  "estimated_fluid_ml": 150,
  "hd_status": "perhatian",
  "history_id": 42
}
```

| Field | Description |
| :--- | :--- |
| `prediction` | Nama makanan/minuman yang terdeteksi |
| `confidence` | Tingkat kepercayaan AI (0.0 – 1.0) |
| `nutrition` | Data nutrisi makanan |
| `estimated_fluid_ml` | Estimasi kandungan cairan |
| `hd_status` | Status untuk pasien HD: `"aman"`, `"perhatian"`, `"hindari"` |
| `history_id` | ID record yang tersimpan di history |

**Error — `400 Bad Request`** (tidak ada gambar)

```json
{
  "image": ["Image file is required."]
}
```

---

### 5.2 `POST /api/scan/urine/`

Scan gambar urine untuk estimasi volume. **Membutuhkan autentikasi.**

**Content-Type:** `multipart/form-data`

**Request Fields**

| Field | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| `image` | `file` | ✅ | File gambar wadah urine |
| `patient_id` | `integer` | ❌ | ID pasien (validasi kepemilikan) |

**Request Example**

```
POST /api/scan/urine/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data

image=<file_binary>
```

**Response — `200 OK`**

```json
{
  "estimated_volume_ml": 420,
  "confidence": 0.88
}
```

> Setelah scan berhasil, sistem akan **otomatis memperbarui** `urine_output_24h_ml` dan menghitung ulang `daily_fluid_limit_ml` pasien.

**Error — `400 Bad Request`**

```json
{
  "image": ["Image file is required."]
}
```

---

## 6. Nutrition / Nutrisi

### 6.1 `GET /api/nutrition/foods/`

Mendapatkan daftar item makanan/minuman. Tidak membutuhkan autentikasi.

**Query Parameters**

| Parameter | Type | Description |
| :--- | :---: | :--- |
| `q` | `string` | Filter berdasarkan nama (case-insensitive) |
| `status` | `string` | Filter berdasarkan HD status: `aman`, `perhatian`, `hindari` |

**Request Example**

```
GET /api/nutrition/foods/?q=nasi&status=aman
```

**Response — `200 OK`**

```json
[
  {
    "id": 1,
    "name": "Nasi Putih",
    "image": "http://localhost:8000/media/food/nasi_putih.jpg",
    "potassium": "55.00",
    "phosphorus": "43.00",
    "sodium": "1.00",
    "hd_status": "aman",
    "description": "Sumber karbohidrat utama, rendah kalium dan fosfor."
  },
  {
    "id": 7,
    "name": "Nasi Tim",
    "image": "http://localhost:8000/media/food/nasi_tim.jpg",
    "potassium": "40.00",
    "phosphorus": "38.00",
    "sodium": "1.00",
    "hd_status": "aman",
    "description": "Nasi lembut, mudah dicerna."
  }
]
```

---

## 7. Education / Edukasi

### 7.1 `GET /api/education/modules/`

Mendapatkan daftar modul edukasi yang dipublish. Tidak membutuhkan autentikasi.

**Request Example**

```
GET /api/education/modules/
```

**Response — `200 OK`**

```json
[
  {
    "title": "Mengelola Cairan untuk Pasien HD",
    "thumbnail": "http://localhost:8000/media/education/cairan_hd.jpg",
    "content": "Pasien hemodialisis perlu membatasi asupan cairan harian karena ginjal tidak lagi mampu membuang kelebihan cairan secara efektif..."
  },
  {
    "title": "Makanan yang Harus Dihindari",
    "thumbnail": "http://localhost:8000/media/education/makanan_hd.jpg",
    "content": "Beberapa makanan tinggi kalium dan fosfor harus dibatasi, termasuk pisang, tomat, dan produk susu..."
  }
]
```

---

## 8. History / Riwayat

### 8.1 `GET /api/history/`

Mendapatkan riwayat aktivitas cairan pasien. **Membutuhkan autentikasi.**

**Query Parameters**

| Parameter | Type | Description |
| :--- | :---: | :--- |
| `date` | `string` | Tanggal dalam format `YYYY-MM-DD` (default: hari ini) |

**Request Example**

```
GET /api/history/?date=2025-05-28
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response — `200 OK`**

```json
[
  {
    "time": "14:30",
    "type": "drink",
    "name": "Air Putih",
    "amount": "200ml",
    "source": "manual"
  },
  {
    "time": "12:00",
    "type": "food",
    "name": "Nasi Goreng",
    "amount": "150ml",
    "source": "scan"
  },
  {
    "time": "07:00",
    "type": "urine",
    "name": "Urine scan (AI)",
    "amount": "400ml",
    "source": "scan"
  }
]
```

| Field | Description |
| :--- | :--- |
| `time` | Waktu pencatatan (format `HH:MM`, zona waktu lokal) |
| `type` | Kategori: `drink`, `food`, atau `urine` |
| `name` | Deskripsi item |
| `amount` | Volume dalam ml |
| `source` | Sumber pencatatan: `manual` atau `scan` |

**Error — `400 Bad Request`** (format tanggal salah)

```json
{
  "date": ["Use YYYY-MM-DD format."]
}
```

---

## 9. Error Responses

### Standard Error Format

Semua error mengikuti format standar Django REST Framework:

```json
{
  "field_name": ["Error message."]
}
```

atau untuk error non-field:

```json
{
  "non_field_errors": ["Error message."]
}
```

### HTTP Status Codes

| Status Code | Keterangan |
| :---: | :--- |
| `200 OK` | Request berhasil |
| `201 Created` | Resource berhasil dibuat |
| `400 Bad Request` | Validasi gagal atau request tidak valid |
| `401 Unauthorized` | Token tidak ada atau tidak valid |
| `403 Forbidden` | Tidak memiliki izin (mis. akses data pasien lain) |
| `404 Not Found` | Resource tidak ditemukan |
| `500 Internal Server Error` | Kesalahan server |

### Error `401 Unauthorized` (Token tidak valid/kadaluarsa)

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

### Error `403 Forbidden` (Bukan akun pasien)

```json
{
  "detail": "Patient profile not found for this account."
}
```

---

## Demo Credentials

| Role | Email / ID | Password |
| :--- | :--- | :--- |
| Pasien (Mobile) | `budi.santoso@dialife.local` | `patient123` |
| Perawat (Web) | `DI-000001` | `nurse123` |

---

*Generated from `core/api_urls.py`, `core/mobile_api.py`, `core/mobile_serializers.py`*
