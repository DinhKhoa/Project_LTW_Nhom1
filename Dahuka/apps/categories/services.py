from django.core.paginator import Paginator
from django.db.models import Q
from .models import DanhMuc

class DanhMucService:
    @staticmethod
    def get_danh_mucs(query='', page_number=1, per_page=10):
        danh_mucs = DanhMuc.objects.all()
        if query:
            danh_mucs = danh_mucs.filter(
                Q(ma_danh_muc__icontains=query) | Q(ten_danh_muc__icontains=query)
            )
        paginator = Paginator(danh_mucs, per_page)
        return paginator.get_page(page_number)

    @staticmethod
    def validate_and_create(ma_danh_muc, ten_danh_muc):
        errors = {}
        if not ma_danh_muc:
            errors['ma_danh_muc'] = 'Vui lòng nhập mã danh mục'
        elif DanhMuc.objects.filter(ma_danh_muc=ma_danh_muc).exists():
            errors['ma_danh_muc'] = 'Mã danh mục đã tồn tại'

        if not ten_danh_muc:
            errors['ten_danh_muc'] = 'Vui lòng nhập tên danh mục'

        if not errors:
            danh_muc = DanhMuc.objects.create(ma_danh_muc=ma_danh_muc, ten_danh_muc=ten_danh_muc)
            return True, danh_muc, errors
        return False, None, errors

    @staticmethod
    def validate_and_update(pk, ma_danh_muc, ten_danh_muc):
        errors = {}
        if not ma_danh_muc:
            errors['ma_danh_muc'] = 'Vui lòng nhập mã danh mục'
        elif DanhMuc.objects.filter(ma_danh_muc=ma_danh_muc).exclude(pk=pk).exists():
            errors['ma_danh_muc'] = 'Mã danh mục đã tồn tại'

        if not ten_danh_muc:
            errors['ten_danh_muc'] = 'Vui lòng nhập tên danh mục'

        if not errors:
            danh_muc = DanhMuc.objects.get(pk=pk)
            danh_muc.ma_danh_muc = ma_danh_muc
            danh_muc.ten_danh_muc = ten_danh_muc
            danh_muc.save()
            return True, danh_muc, errors
        return False, None, errors

    @staticmethod
    def format_products_for_dropdown(danh_muc, query_ma=''):
        san_phams = danh_muc.sanpham_set.all()
        if query_ma:
            san_phams = san_phams.filter(ma_san_pham__icontains=query_ma)

        products = []
        for sp in san_phams:
            products.append({
                'ma_san_pham': sp.ma_san_pham,
                'ten_san_pham': sp.ten_san_pham,
                'gia_tien': f"{sp.gia_tien:,.0f}".replace(",", ".") + " đ",
                'ton_kho': sp.ton_kho if sp.ton_kho >= 0 else '∞',
                'trang_thai_ton_kho': sp.trang_thai_ton_kho,
                'trang_thai_ton_kho_display': sp.trang_thai_ton_kho_display,
                'trang_thai_hien_thi': sp.trang_thai_hien_thi,
                'danh_muc': sp.danh_muc.ten_danh_muc,
            })
        return products
