import pandas as pd
from core.models import FoodItem

class FoodImportService:
    @staticmethod
    def normalize_number(value):
        if pd.isna(value) or value in [None, "", "-"]:
            return 0
        try:
            return float(str(value).replace(",", "."))
        except:
            return 0

    @staticmethod
    def import_file(file):
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            raise ValueError("Unsupported file format")

        created_count = 0
        updated_count = 0
        skipped_count = 0

        # Optional lowercasing of columns to handle various formats
        df.columns = [str(c).lower().strip() for c in df.columns]

        for index, row in df.iterrows():
            # Get name from variations of column header
            name = row.get('name') or row.get('food_name')
            if not name or pd.isna(name):
                skipped_count += 1
                continue
            
            name = str(name).strip()
            
            # Map values
            calories = int(FoodImportService.normalize_number(row.get('calories', 0)))
            protein = FoodImportService.normalize_number(row.get('proteins') or row.get('protein') or 0)
            sodium = int(FoodImportService.normalize_number(row.get('natrium', 0)))
            potassium = int(FoodImportService.normalize_number(row.get('kalium', 0)))
            phosphorus = int(FoodImportService.normalize_number(row.get('fosfor', 0)))
            cairan = int(FoodImportService.normalize_number(row.get('cairan', 0)))
            
            # HD status
            hd = str(row.get('status hd', 'Aman')).strip().lower()
            if hd not in ['aman', 'batasi', 'hindari']:
                hd = 'aman'
                
            image_name = str(row.get('image', '')).strip() if pd.notna(row.get('image')) else ''
            
            kategori = str(row.get('kategori klinis', '')).strip() if pd.notna(row.get('kategori klinis')) else ''
            porsi = str(row.get('porsi saji', '')).strip() if pd.notna(row.get('porsi saji')) else ''
            
            desc = []
            if kategori:
                desc.append(f"Kategori Klinis: {kategori}")
            if porsi:
                desc.append(f"Porsi Saji: {porsi}")
            
            defaults = {
                'calories': calories,
                'protein': protein,
                'sodium': sodium,
                'potassium': potassium,
                'phosphorus': phosphorus,
                'estimated_fluid_ml': cairan,
                'hd_status': hd,
                'image_name': image_name,
                'description': "\n".join(desc),
                'is_active': True
            }

            obj, created = FoodItem.objects.update_or_create(
                name=name,
                defaults=defaults
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1

        return {
            'total': len(df),
            'created': created_count,
            'updated': updated_count,
            'skipped': skipped_count
        }

    @staticmethod
    def import_images(file):
        """Import image URLs from an Excel file, updating only image_name on matching FoodItems.
        
        Expected columns: name, image_url
        Matching is case-insensitive by food name.
        """
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            raise ValueError("Unsupported file format")

        df.columns = [str(c).lower().strip() for c in df.columns]

        updated_count = 0
        skipped_count = 0
        not_found_names = []

        for index, row in df.iterrows():
            name = row.get('name') or row.get('food_name')
            if not name or pd.isna(name):
                skipped_count += 1
                continue

            name = str(name).strip()

            image_url = row.get('image_url') or row.get('image_name') or row.get('image')
            if not image_url or pd.isna(image_url):
                skipped_count += 1
                continue

            image_url = str(image_url).strip()

            # Case-insensitive match by name
            try:
                food = FoodItem.objects.get(name__iexact=name, is_active=True)
                food.image_name = image_url
                food.save(update_fields=['image_name'])
                updated_count += 1
            except FoodItem.DoesNotExist:
                not_found_names.append(name)
                skipped_count += 1
            except FoodItem.MultipleObjectsReturned:
                # Update all matching items
                foods = FoodItem.objects.filter(name__iexact=name, is_active=True)
                foods.update(image_name=image_url)
                updated_count += foods.count()

        return {
            'total': len(df),
            'updated': updated_count,
            'skipped': skipped_count,
            'not_found': not_found_names
        }
