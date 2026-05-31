# Admin Portal Implementation Plan (Django)

## Overview

Saat ini sistem memiliki portal login untuk Nurse. Akan ditambahkan **Admin Portal** pada URL yang sama tanpa menggunakan Django `/admin`.

Ketika user login:

* Jika `is_superuser=True` → redirect ke **Admin Dashboard**
* Jika user Nurse → tetap masuk ke portal Nurse seperti saat ini

Admin Portal menggunakan template custom sendiri dan tidak menggunakan Django Admin bawaan.

---

# Authentication Flow

## Login Flow

### Existing

```
/login
```

### New Behavior

```python
if request.user.is_superuser:
    redirect("admin_dashboard")
else:
    redirect("nurse_dashboard")
```

---

# Admin Layout

## URL Prefix

```
/dashboard/admin/
/dashboard/admin/patients/
/dashboard/admin/nurses/
/dashboard/admin/foods/
/dashboard/admin/education-modules/
```

## Base Template

Create:

```
templates/
└── admin_portal/
    ├── base.html
    ├── dashboard.html
    ├── patients/
    ├── nurses/
    ├── foods/
    └── education_modules/
```

---

# Sidebar Menu

## Dashboard

* Dashboard
* Patients
* Nurses
* Foods
* Education Modules
* Logout

---

# Dashboard Page

## Statistics Cards

Show:

### Patients

```
Total Patients
```

### Nurses

```
Total Nurses
```

### Foods

```
Total Foods
```

### Education Modules

```
Total Modules
```

### Recent Activity

Display:

* latest patient created
* latest nurse created
* latest food imported

---

# Patients Module

## Menu

```
Patients
```

## Features

### List

* Pagination
* Search

Search fields:

* name
* email
* phone

### Create

Fields:

* full_name
* email
* phone
* gender
* birth_date

### Detail

View patient detail

### Edit

Update patient

### Delete

Soft delete preferred

---

# Nurses Module

## Menu

```
Nurses
```

## Features

### List

* Pagination
* Search

Search fields:

* name
* email

### Create

Fields:

* name
* email
* password

System automatically creates User account.

### Edit

Update nurse profile

### Delete

Soft delete preferred

### Reset Password

Admin can reset nurse password.

---

# Food Module

## Menu

```
Foods
```

## Features

### List

* Pagination
* Search

Search fields:

* food_name
* category

### Create

### Edit

### Delete

### Detail

Display nutrition information.

---

# Food Import Feature

## Supported Files

* .xlsx
* .xls
* .csv

Libraries:

```bash
pip install pandas openpyxl xlrd
```

---

# Import UI

Button:

```
Import Food Data
```

Upload file:

```
Choose File
Import
```

---

# CSV Mapping

Expected columns:

| CSV Column   | Model Field  |
| ------------ | ------------ |
| name         | food_name    |
| calories     | calories     |
| protein      | protein      |
| fat          | fat          |
| carbohydrate | carbohydrate |
| water        | water        |
| fiber        | fiber        |

Mapping can be adjusted based on actual CSV.

---

# Data Normalization

Problem:

```
Line number: 1
Field 'calories' expected a number but got '280.0'
```

Cause:

CSV value stored as string.

Example:

```python
"280.0"
```

while model expects:

```python
IntegerField
```

---

# Solution

Before save:

```python
def normalize_number(value):
    if value in [None, "", "-"]:
        return 0

    try:
        return float(str(value).replace(",", "."))
    except:
        return 0
```

Usage:

```python
food.calories = int(normalize_number(row["calories"]))
food.protein = normalize_number(row["protein"])
food.fat = normalize_number(row["fat"])
food.carbohydrate = normalize_number(row["carbohydrate"])
```

---

# Import Service Layer

Create:

```python
services/food_import_service.py
```

Example:

```python
class FoodImportService:

    @staticmethod
    def import_file(file):
        ...
```

Responsibilities:

* read csv/xlsx
* normalize data
* validate columns
* save/update food records
* return summary

---

# Import Result

After upload show:

```text
Import Completed

Rows Processed : 1200
Created : 1100
Updated : 80
Skipped : 20
```

---

# Duplicate Handling

Food uniqueness:

```python
food_name
```

Logic:

```python
Food.objects.update_or_create(
    food_name=row["food_name"],
    defaults={
        ...
    }
)
```

---

# Education Modules

## Menu

```
Education Modules
```

## Features

### List

* Pagination
* Search

Search by:

* title

### Create

Fields:

* title
* description
* content
* thumbnail
* status

### Edit

### Delete

### Detail

### Publish / Unpublish

```python
status = DRAFT
status = PUBLISHED
```

---

# Permissions

Decorator:

```python
@user_passes_test(lambda u: u.is_superuser)
```

or

```python
class SuperAdminRequiredMixin
```

All admin pages must require:

```python
is_authenticated
is_superuser
```

---

# Suggested Structure

```text
apps/
├── admin_portal/
│
├── patients/
│
├── nurses/
│
├── foods/
│
└── education_modules/
```

---

# Deliverables

## Authentication

* [ ] Superuser redirect
* [ ] Admin dashboard
* [ ] Permission middleware

## Patients

* [ ] CRUD
* [ ] Search
* [ ] Pagination

## Nurses

* [ ] CRUD
* [ ] Search
* [ ] Reset password

## Foods

* [ ] CRUD
* [ ] Search
* [ ] Pagination
* [ ] Import CSV
* [ ] Import XLS
* [ ] Import XLSX
* [ ] Data normalization
* [ ] Duplicate handling

## Education Modules

* [ ] CRUD
* [ ] Search
* [ ] Publish/Unpublish

## UI

* [ ] Admin sidebar
* [ ] Dashboard cards
* [ ] Responsive layout
* [ ] Consistent styling with Nurse Portal

```
```
