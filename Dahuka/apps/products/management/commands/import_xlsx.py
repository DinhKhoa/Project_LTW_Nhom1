import os
import requests
import pandas as pd
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.categories.models import Category
from apps.products.models import Product, ProductImage
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Import products and images from XLSX files (Sanpham.xlsx and hinhanhsanpham.xlsx)'

    def handle(self, *args, **options):
        self.stdout.write("Starting import...")
        self.import_products()
        self.import_images()
        self.stdout.write(self.style.SUCCESS('Successfully imported all Excel data'))

    def download_image(self, url, filename):
        if not url or pd.isna(url) or not str(url).startswith('http'):
            return None
        try:
            # Add some headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, timeout=15, headers=headers)
            if response.status_code == 200:
                return ContentFile(response.content, name=filename)
            else:
                self.stdout.write(self.style.WARNING(f"Failed to download {url}: Status {response.status_code}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error downloading {url}: {e}"))
        return None

    def import_products(self):
        self.stdout.write("Reading Sanpham.xlsx...")
        df = pd.read_excel('Sanpham.xlsx')
        count = 0
        for index, row in df.iterrows():
            sku = str(row.get('MaSP', '')).strip()
            if not sku or pd.isna(sku) or sku == 'nan':
                continue

            # Get Category
            cat_id = row.get('MaDMSP')
            category = None
            if not pd.isna(cat_id):
                try:
                    category = Category.objects.get(id=int(cat_id))
                except (Category.DoesNotExist, ValueError):
                    pass
            
            if not category:
                # Fallback: find any category or create a default one
                category = Category.objects.first()
                if not category:
                    category = Category.objects.create(name="Chưa phân loại", slug="chua-phan-loai")

            # Clean price
            price = row.get('Gia', 0)
            if pd.isna(price):
                price = 0
            else:
                try:
                    # If it's a string, clean all non-numeric characters except dots or commas
                    if isinstance(price, str):
                        import re
                        # Keep only digits
                        price = re.sub(r'[^\d]', '', price)
                    
                    if not price:
                        price = 0
                    else:
                        price = float(price)
                except (ValueError, TypeError):
                    price = 0

            # Product data mapping
            defaults = {
                'category': category,
                'name': str(row.get('TenSP', '')),
                'description': str(row.get('MoTaChiTiet', '') if not pd.isna(row.get('MoTaChiTiet')) else ''),
                'short_description': str(row.get('MoTa', '') if not pd.isna(row.get('MoTa')) else ''),
                'price': price,
                'spec_power': str(row.get('CongSuatLoc', '') if not pd.isna(row.get('CongSuatLoc')) else ''),
                'spec_technology': str(row.get('CongNgheLoc', '') if not pd.isna(row.get('CongNgheLoc')) else ''),
                'spec_dimensions': str(row.get('KichThuoc', '') if not pd.isna(row.get('KichThuoc')) else ''),
                'spec_type': str(row.get('LoaiMay', '') if not pd.isna(row.get('LoaiMay')) else ''),
                'spec_capacity': str(row.get('DungTichBinhChua', '') if not pd.isna(row.get('DungTichBinhChua')) else ''),
                'spec_hot_temp': str(row.get('NhietDoNuocNong', '') if not pd.isna(row.get('NhietDoNuocNong')) else ''),
                'spec_cold_temp': str(row.get('NhietDoNuocLanh', '') if not pd.isna(row.get('NhietDoNuocLanh')) else ''),
                'spec_release_year': str(row.get('NamRaMat', '') if not pd.isna(row.get('NamRaMat')) else ''),
                'spec_filters_count': str(row.get('SoLoiLoc', '') if not pd.isna(row.get('SoLoiLoc')) else ''),
                'spec_weight': str(row.get('KhoiLuong', '') if not pd.isna(row.get('KhoiLuong')) else ''),
                'spec_origin': str(row.get('NoiSX', '') if not pd.isna(row.get('NoiSX')) else ''),
                'spec_warranty': str(row.get('ThoiGianBH', '') if not pd.isna(row.get('ThoiGianBH')) else ''),
                'spec_features': str(row.get('TinhNang', '') if not pd.isna(row.get('TinhNang')) else ''),
                'spec_other': str(row.get('ThongTinSanPham', '') if not pd.isna(row.get('ThongTinSanPham')) else ''),
                'is_active': True,
            }

            product, created = Product.objects.update_or_create(sku=sku, defaults=defaults)
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} product: {sku}")
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Imported {count} products"))

    def import_images(self):
        self.stdout.write("Reading hinhanhsanpham.xlsx...")
        df = pd.read_excel('hinhanhsanpham.xlsx')
        count = 0
        for index, row in df.iterrows():
            sku = str(row.get('MaSP', '')).strip()
            if not sku or pd.isna(sku) or sku == 'nan':
                continue

            try:
                product = Product.objects.get(sku=sku)
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  Product {sku} not found for image import"))
                continue

            # Main Image
            main_url = row.get('AnhChinh')
            if main_url and not pd.isna(main_url):
                # Only download if product doesn't have an image or we want to force update
                image_file = self.download_image(main_url, f"{sku}_main.jpg")
                if image_file:
                    product.image.save(f"{sku}_main.jpg", image_file, save=True)
                    self.stdout.write(f"    Saved main image for {sku}")

            # Gallery Images
            gallery_urls = {
                'AnhPhu1': 'gallery',
                'AnhPhu2': 'gallery',
                'AnhTinhNang': 'features',
                'AnhMoTa': 'description'
            }

            for col, img_type in gallery_urls.items():
                url = row.get(col)
                if url and not pd.isna(url):
                    # For gallery images, we match by product and image_type and caption
                    image_file = self.download_image(url, f"{sku}_{col}.jpg")
                    if image_file:
                        ProductImage.objects.update_or_create(
                            product=product,
                            image_type=img_type,
                            caption=f"Image {col}",
                            defaults={'image_url': image_file}
                        )
                        self.stdout.write(f"    Saved {img_type} image ({col}) for {sku}")
            
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Imported images for {count} products"))
