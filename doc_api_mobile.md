API mobile HD Care dari PRD sudah diterapkan ke proyek. Ringkasan perubahan:

Struktur URL
PRD	Implementasi
/api/...
Mobile (pasien / Flutter)
/api/v1/nurse/...
API perawat (dashboard web, Token auth)
Endpoint mobile (sesuai PRD)
Endpoint	Fungsi
POST /api/auth/register/
Daftar pasien
POST /api/auth/login/
Login → access_token, refresh_token, user
POST /api/auth/refresh/
Refresh JWT (refresh atau refresh_token)
POST /api/logout/
Blacklist refresh token
GET /api/profile/
Profil pasien
PATCH /api/profile/update/
Update profil
GET /api/dashboard/home/
Beranda (cairan + today_summary)
POST /api/fluid/calculate/
Kalkulator: urine + 500 ml
POST /api/fluid/intake/
Catat cairan manual
POST /api/scan/food-drink/
Scan makanan/minuman (multipart)
POST /api/scan/urine/
Scan urine (multipart)
GET /api/nutrition/foods/
Daftar nutrisi
GET /api/education/modules/
Modul edukasi
GET /api/history/
Riwayat aktivitas
Model baru
UserProfile (role: patient / nurse)
Patient.user — akun mobile pasien
FoodItem, FoodScanHistory, UrineScanHistory, EducationModule
Auth
JWT (Bearer) untuk mobile
Token tetap untuk nurse API di /api/v1/nurse/
AI scan (MVP)
core/services/scan_service.py — validasi gambar + lookup nutrisi dari DB (siap diganti TensorFlow/OpenCV)
Hasil scan disimpan ke history & memperbarui intake pasien
Setup
cd c:\Users\Impacto\Documents\DIALIFE\dialife
pip install djangorestframework-simplejwt Pillow
python manage.py makemigrations core
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
Akun demo mobile: budi.santoso@dialife.local / patient123
Nurse web: DI-000001 / nurse123

Contoh Flutter
Login:

POST /api/auth/login/
{ "email": "budi.santoso@dialife.local", "password": "patient123" }
Header: Authorization: Bearer <access_token>

Beranda:

GET /api/dashboard/home/
Scan makanan:

POST /api/scan/food-drink/
Form: image=<file>, patient_id=<optional>
File utama: core/mobile_api.py, core/mobile_serializers.py, core/api_urls.py, core/services/.

Jika Anda mau, langkah berikutnya bisa menambah integrasi model TensorFlow nyata atau dokumentasi OpenAPI untuk tim Flutter.