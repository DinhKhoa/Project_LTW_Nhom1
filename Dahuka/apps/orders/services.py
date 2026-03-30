from django.core.paginator import Paginator
from django.db.models import Q
from .models import DonDatHang

class OrderService:
    @staticmethod
    def get_don_hangs(query='', trang_thai_filter='', page_number=1, per_page=5):
        don_hangs = DonDatHang.objects.all()

        if query:
            don_hangs = don_hangs.filter(
                Q(ma_don_hang__icontains=query) | Q(ho_ten__icontains=query)
            )

        if trang_thai_filter:
            don_hangs = don_hangs.filter(trang_thai=trang_thai_filter)

        paginator = Paginator(don_hangs, per_page)
        return paginator.get_page(page_number)

    @staticmethod
    def handle_order_action(don_hang, action, nhan_vien=''):
        if action == 'xac_nhan':
            don_hang.trang_thai = 'da_xac_nhan'
            don_hang.save()
        elif action == 'dang_giao':
            don_hang.trang_thai = 'dang_giao_hang'
            don_hang.save()
        elif action == 'giao_thanh_cong':
            don_hang.trang_thai = 'giao_hang_thanh_cong'
            don_hang.trang_thai_thanh_toan = 'da_thanh_toan'
            don_hang.save()
        elif action == 'huy_don':
            don_hang.trang_thai = 'da_huy'
            don_hang.save()
        elif action == 'luu_thay_doi':
            don_hang.nhan_vien_phu_trach = nhan_vien
            don_hang.save()
        return don_hang

    @staticmethod
    def calc_current_step(don_hang):
        trang_thai_steps = ['cho_xac_nhan', 'da_xac_nhan', 'dang_giao_hang', 'giao_hang_thanh_cong']
        if don_hang.trang_thai in trang_thai_steps:
            return trang_thai_steps.index(don_hang.trang_thai)
        return 0
