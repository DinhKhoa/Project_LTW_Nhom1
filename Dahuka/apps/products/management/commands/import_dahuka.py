import csv
import ast
from django.core.management.base import BaseCommand
from apps.categories.models import Category
from apps.products.models import Product, ProductImage

class Command(BaseCommand):
    help = 'Import categories and products from CSV files'

    def handle(self, *args, **options):
        self.import_categories()
        self.import_products()
        self.import_images()
        self.stdout.write(self.style.SUCCESS('Successfully imported all data'))

    def import_categories(self):
        with open('DanhMucSP.csv', mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            self.stdout.write(f"Headers in DanhMucSP: {reader.fieldnames}")
            for row in reader:
                name = row.get('TenDM')
                if not name: continue
                Category.objects.get_or_create(name=name)
        self.stdout.write('Imported categories')

    def import_products(self):
        # Category map for quick lookup by name
        cat_name_map = {c.name.lower(): c for c in Category.objects.all()}
        
        with open('SanPham.csv', mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            self.stdout.write(f"Headers in SanPham: {reader.fieldnames}")
            count = 0
            for row in reader:
                name = row.get('TenSP')
                if not name: continue 
                
                price_str = row.get('GiaTien', '0').replace(',', '').replace('đ', '').strip()
                try:
                    price = int(price_str)
                except ValueError:
                    price = 0
                
                # Try to map category if possible (this script is old, might not have it)
                category = None
                # ... skipping complex mapping for legacy script
                
                product, created = Product.objects.update_or_create(
                    name=name,
                    defaults={
                        'category': category,
                        'price': price,
                        'description': row.get('ThongSo') or row.get('MoTaNgan') or '',
                        'short_description': row.get('MoTaNgan') or '',
                        'stock': int(row['SoLuongTon']) if row.get('SoLuongTon') else 100,
                        'is_active': row.get('TrangThaiHienThi') == 'Hiển thị',
                        'spec_power': row.get('CongSuatLoc') or '',
                        'spec_technology': row.get('CongNgheLoc') or '',
                        'spec_dimensions': row.get('KichThuoc') or '',
                        'spec_type': row.get('LoaiMay') or '',
                        'spec_capacity': row.get('DungTichBinh') or '',
                        'spec_hot_temp': row.get('NhietDoNong') or '',
                        'spec_cold_temp': row.get('NhietDoLanh') or '',
                        'spec_release_year': row.get('NamRaMat') or '',
                        'spec_origin': row.get('NoiSanXuat') or '',
                        'spec_filters_count': row.get('SoLoiLoc') or '',
                        'spec_weight': row.get('KhoiLuong') or '',
                        'spec_warranty': row.get('ThoiGianBaoHanh') or '',
                        'spec_water_source': row.get('LoaiNguonNuoc') or '',
                        'spec_features': row.get('TinhNang') or '',
                        'spec_other': row.get('ThongSo') or '',
                    }
                )
                count += 1
                
                # Handle ImageUrls from SanPham.csv too
                urls_str = row.get('ImageUrls')
                if urls_str:
                    try:
                        urls = ast.literal_eval(urls_str)
                        if isinstance(urls, list):
                            for url in urls:
                                ProductImage.objects.get_or_create(
                                    product=product,
                                    image_url=url
                                )
                    except:
                        pass
                        
        self.stdout.write(f'Imported {count} products')

    def import_images(self):
        # We'll skip additional image import for this legacy script as it depends on SKU
        self.stdout.write('Skipping additional image import for legacy script (no SKU mapping)')
