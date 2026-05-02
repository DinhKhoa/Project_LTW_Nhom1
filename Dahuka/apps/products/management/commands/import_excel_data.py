import os
import pandas as pd
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from apps.categories.models import Category
from apps.products.models import Product, ProductImage
from django.db import transaction

class Command(BaseCommand):
    help = 'Import data from Excel file databasecuoiky (1).xlsx (Updated to remove SKU/Code)'

    def handle(self, *args, **options):
        file_path = os.path.join(os.getcwd(), 'databasecuoiky (1).xlsx')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        self.stdout.write(self.style.SUCCESS('Starting import...'))

        try:
            # Load sheets
            df_categories = pd.read_excel(file_path, sheet_name='DanhMucSP')
            df_products = pd.read_excel(file_path, sheet_name='SanPham')
            df_images = pd.read_excel(file_path, sheet_name='HinhAnhSanPham')

            with transaction.atomic():
                # 1. Import Categories
                self.stdout.write('Importing Categories...')
                category_map = {} # Excel MaDMSP -> Category object
                for _, row in df_categories.iterrows():
                    excel_cat_code = str(row['MaDMSP'])
                    name = str(row['TenDM'])
                    # Use name as unique identifier in our system now
                    category, created = Category.objects.update_or_create(
                        name=name,
                        defaults={'slug': slugify(name)}
                    )
                    category_map[excel_cat_code] = category
                    
                    # Also map the numeric part if exists (e.g. "MaDM_001" -> "1")
                    import re
                    match = re.search(r'(\d+)', excel_cat_code)
                    if match:
                        numeric_code = str(int(match.group(1)))
                        category_map[numeric_code] = category
                        
                    if created:
                        self.stdout.write(f'  Created category ID: {category.id}')

                # 2. Import Products
                self.stdout.write('Importing Products...')
                product_map = {} # Excel MaSP -> Product object
                for _, row in df_products.iterrows():
                    excel_sp_code = str(row['MaSP'])
                    cat_code = str(row['MaDMSP'])
                    
                    if cat_code not in category_map:
                        try:
                            cat_code = str(int(float(cat_code)))
                        except:
                            pass
                    
                    if cat_code not in category_map:
                        self.stdout.write(self.style.WARNING(f'  Skipping product {excel_sp_code}: Category {cat_code} not found'))
                        continue
                    
                    category = category_map[cat_code]
                    product_name = str(row['TenSP'])
                    
                    # Clean price
                    price_str = str(row['Gia'])
                    price = 0
                    try:
                        price_digits = ''.join(filter(str.isdigit, price_str))
                        if price_digits:
                            price = int(price_digits)
                    except:
                        pass

                    # Prepare product data
                    product_data = {
                        'category': category,
                        'short_description': str(row['ThongTinSanPham']) if pd.notna(row['ThongTinSanPham']) else "",
                        'description': (str(row['MoTa']) if pd.notna(row['MoTa']) else "") + "\n" + (str(row['MoTaChiTiet']) if pd.notna(row['MoTaChiTiet']) else ""),
                        'spec_features': str(row['TinhNang']) if pd.notna(row['TinhNang']) else "",
                        'spec_power': str(row['CongSuatLoc']) if pd.notna(row['CongSuatLoc']) else "",
                        'spec_type': str(row['LoaiMay']) if pd.notna(row['LoaiMay']) else "",
                        'spec_technology': str(row['CongNgheLoc']) if pd.notna(row['CongNgheLoc']) else "",
                        'spec_capacity': str(row['DungTichBinhChua']) if pd.notna(row['DungTichBinhChua']) else "",
                        'spec_hot_temp': str(row['NhietDoNuocNong']) if pd.notna(row['NhietDoNuocNong']) else "",
                        'spec_cold_temp': str(row['NhietDoNuocLanh']) if pd.notna(row['NhietDoNuocLanh']) else "",
                        'spec_release_year': str(row['NamRaMat']) if pd.notna(row['NamRaMat']) else "",
                        'spec_filters_count': str(row['SoLoiLoc']) if pd.notna(row['SoLoiLoc']) else "",
                        'spec_dimensions': str(row['KichThuoc']) if pd.notna(row['KichThuoc']) else "",
                        'spec_weight': str(row['KhoiLuong']) if pd.notna(row['KhoiLuong']) else "",
                        'spec_origin': str(row['NoiSX']) if pd.notna(row['NoiSX']) else "",
                        'spec_warranty': str(row['ThoiGianBH']) if pd.notna(row['ThoiGianBH']) else "",
                        'price': price,
                        'slug': slugify(product_name)
                    }

                    # Use name as identifier
                    product, created = Product.objects.update_or_create(
                        name=product_name,
                        defaults=product_data
                    )
                    product_map[excel_sp_code] = product
                    if created:
                        self.stdout.write(f'  Created product ID: {product.id}')
                    else:
                        self.stdout.write(f'  Updated product ID: {product.id}')

                # 3. Import Images
                self.stdout.write('Importing Product Images...')
                for _, row in df_images.iterrows():
                    excel_sp_code = str(row['MaSP'])
                    if excel_sp_code not in product_map:
                        continue
                    
                    product = product_map[excel_sp_code]
                    
                    image_mappings = [
                        ('AnhChinh', 'main'),
                        ('AnhPhu1', 'gallery'),
                        ('AnhPhu2', 'gallery'),
                        ('AnhTinhNang', 'features'),
                        ('AnhMoTa', 'description'),
                    ]

                    for col_name, img_type in image_mappings:
                        img_url = row[col_name]
                        if pd.isna(img_url) or not str(img_url).startswith('http'):
                            continue
                        
                        self.download_and_save_image(product, str(img_url), img_type)

            self.stdout.write(self.style.SUCCESS('Import completed successfully!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())

    def download_and_save_image(self, product, url, img_type):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Use product.id instead of sku for filename
                file_name = f"prod_{product.id}_{img_type}_{os.path.basename(url.split('?')[0])}"
                content = ContentFile(response.content)
                
                if img_type == 'main':
                    if not product.image:
                        product.image.save(file_name, content, save=True)
                        self.stdout.write(f'    Saved main image for ID: {product.id}')
                else:
                    ProductImage.objects.create(
                        product=product,
                        image_url=None,
                        caption=f"Image from Excel: {img_type}"
                    ).image_url.save(file_name, content, save=True)
                    self.stdout.write(f'    Saved {img_type} image for ID: {product.id}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'    Failed to download {url}: {e}'))
