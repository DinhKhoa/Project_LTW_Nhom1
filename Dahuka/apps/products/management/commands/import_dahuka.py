import csv
import ast
import os
from django.core.management.base import BaseCommand
from apps.categories.models import Category
from apps.products.models import Product, ProductImage
from django.utils.text import slugify

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
                code = row.get('MaDM')
                if not name: continue
                Category.objects.update_or_create(
                    name=name,
                    defaults={'code': code}
                )
        self.stdout.write('Imported categories')

    def import_products(self):
        # Category map for quick lookup
        cat_map = {c.code: c for c in Category.objects.all() if c.code}
        cat_name_map = {c.name.lower(): c for c in Category.objects.all()}
        
        with open('SanPham.csv', mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            self.stdout.write(f"Headers in SanPham: {reader.fieldnames}")
            count = 0
            for row in reader:
                sku = row.get('MaSP')
                name = row.get('TenSP')
                if not name or not sku: continue 
                
                price_str = row.get('GiaTien', '0').replace(',', '').replace('đ', '').strip()
                try:
                    price = int(price_str)
                except ValueError:
                    price = 0
                
                cat_code = row.get('MaDM')
                category = cat_map.get(cat_code)
                if not category:
                    # Try to find by name if code mapping failed somehow or is missing
                    # (Fallback)
                    pass

                product, created = Product.objects.update_or_create(
                    sku=sku,
                    defaults={
                        'name': name,
                        'category': category,
                        'price': price,
                        'description': row.get('ThongSo') or row.get('MoTaNgan') or '',
                        'short_description': row.get('MoTaNgan') or '',
                        'stock': int(row['SoLuongTon']) if row.get('SoLuongTon') else 100,
                        'is_active': row.get('TrangThaiHienThi') == 'Hiển thị',
                        'spec_power': row.get('CongSuatLoc') or '',
                        'spec_technology': row.get('CongNgheLoc') or '',
                        'spec_dimensions': row.get('KichThuoc') or '',
                        'spec_loai_may': row.get('LoaiMay') or '',
                        'spec_dung_tich': row.get('DungTichBinh') or '',
                        'spec_nhiet_do_nong': row.get('NhietDoNong') or '',
                        'spec_nhiet_do_lanh': row.get('NhietDoLanh') or '',
                        'spec_nam_ra_mat': row.get('NamRaMat') or '',
                        'spec_noi_san_xuat': row.get('NoiSanXuat') or '',
                        'spec_so_loi_loc': row.get('SoLoiLoc') or '',
                        'spec_khoi_luong': row.get('KhoiLuong') or '',
                        'spec_bao_hanh': row.get('ThoiGianBaoHanh') or '',
                        'spec_nguon_nuoc': row.get('LoaiNguonNuoc') or '',
                        'spec_tinh_nang': row.get('TinhNang') or '',
                        'spec_thong_so_khac': row.get('ThongSo') or '',
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
        with open('HinhAnhSanPham.csv', mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            self.stdout.write(f"Headers in HinhAnhSanPham: {reader.fieldnames}")
            count = 0
            for row in reader:
                sku = row.get('MaSP')
                url = row.get('URL')
                if not sku or not url: continue
                
                try:
                    product = Product.objects.get(sku=sku)
                    ProductImage.objects.get_or_create(
                        product=product,
                        image_url=url,
                        defaults={'caption': row.get('TenAnh', '')}
                    )
                    count += 1
                except Product.DoesNotExist:
                    continue
        self.stdout.write(f'Imported {count} additional images')
