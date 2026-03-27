import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dahuka.settings')
django.setup()

from quanlydanhmuc.models import DanhMuc, SanPham
from quanlydondathang.models import DonDatHang, ChiTietDonHang
from django.utils import timezone
from datetime import timedelta

# Clear existing data
ChiTietDonHang.objects.all().delete()
DonDatHang.objects.all().delete()
SanPham.objects.all().delete()
DanhMuc.objects.all().delete()

# Create categories
categories = [
    ('DM-001', 'Máy lọc nước'),
    ('DM-002', 'Máy lọc nước ion kiềm Hydrogen'),
    ('DM-003', 'Máy lọc nước Probiotics'),
    ('DM-004', 'Máy lọc nước điện giải'),
    ('DM-005', 'Máy lọc nước để gầm'),
    ('DM-006', 'Linh kiện'),
    ('DM-007', 'Dịch vụ'),
]

dm_objects = {}
for code, name in categories:
    dm = DanhMuc.objects.create(ma_danh_muc=code, ten_danh_muc=name)
    dm_objects[code] = dm
    print(f"Created category: {code} - {name}")

# Create products
products = [
    ('MP-S96-001', 'Máy lọc nước RO Mutosi MP-S96', 11645000, 14, True, 'DM-001'),
    ('MP-S66-002', 'Máy lọc nước RO Mutosi MP-S66', 7320000, 36, True, 'DM-001'),
    ('KG-A20-003', 'Máy lọc nước Kangaroo KG-A20', 5211000, 3, True, 'DM-001'),
    ('KG-B15-007', 'Máy lọc nước Kangaroo KG-B15', 4850000, 0, True, 'DM-001'),
    ('MT-RO7-008', 'Máy lọc nước RO Mutosi 7-stage', 8900000, 7, True, 'DM-001'),
    ('MP-P89-010', 'Máy lọc nước điện giải ion kiềm Hydrogen MP-P89K', 15500000, 12, True, 'DM-002'),
    ('MP-T88-011', 'Máy lọc nước điện giải ion kiềm Hydrogen MP-T888', 18200000, 5, True, 'DM-002'),
    ('MP-666-012', 'Máy lọc nước điện giải ion kiềm Hydrogen MP-666', 12800000, 8, True, 'DM-002'),
    ('MP-S10-013', 'Máy lọc nước điện giải ion kiềm Hydrogen MP-S1021H', 22000000, 0, True, 'DM-002'),
    ('PB-M01-014', 'Máy lọc nước Probiotics Mutosi PB-M01', 9500000, 15, True, 'DM-003'),
    ('PB-K02-015', 'Máy lọc nước Probiotics KG-K02', 8200000, 5, True, 'DM-003'),
    ('DG-R01-016', 'Máy lọc nước điện giải Mutosi DG-R01', 14000000, 10, True, 'DM-004'),
    ('DG-T02-017', 'Máy lọc nước điện giải Kangaroo DG-T02', 11500000, 14, True, 'DM-004'),
    ('GM-A01-018', 'Máy lọc nước để gầm Mutosi GM-A01', 6800000, 20, True, 'DM-005'),
    ('GM-K02-019', 'Máy lọc nước để gầm Kangaroo GM-K02', 5500000, 14, True, 'DM-005'),
    ('FLT-7S-004', 'Bộ lọc thay thế Mutosi 7-stage', 450000, 128, True, 'DM-006'),
    ('CRB-1-006', 'Bộ lọc carbon Kangaroo CRB-1', 280000, 0, False, 'DM-006'),
    ('UVL-S1-009', 'Đèn UV diệt khuẩn Mutosi S1', 320000, 52, True, 'DM-006'),
    ('SVC-W3-005', 'Dịch vụ bảo hành mở rộng 3 năm', 1200000, 9999, True, 'DM-007'),
    ('SVC-INS-10', 'Dịch vụ lắp đặt tại nhà', 500000, 9999, True, 'DM-007'),
]

sp_objects = {}
for code, name, price, stock, visible, dm_code in products:
    sp = SanPham.objects.create(
        ma_san_pham=code,
        ten_san_pham=name,
        gia_tien=price,
        ton_kho=stock,
        trang_thai_hien_thi=visible,
        danh_muc=dm_objects[dm_code]
    )
    sp_objects[code] = sp
    print(f"Created product: {code} - {name}")

# Create orders
now = timezone.now()

order1 = DonDatHang.objects.create(
    ma_don_hang='DH20260122008',
    ho_ten='An Nguyễn Văn',
    so_dien_thoai='0349434950',
    dia_chi='68-Dương Khuê, Thành phố Đà Nẵng, Quận Sơn Trà, Phường Phước Mỹ',
    trang_thai='cho_xac_nhan',
    hinh_thuc_thanh_toan='tien_mat',
    trang_thai_thanh_toan='chua_thanh_toan',
    tien_coc=0,
    nhan_vien_phu_trach='',
)

ChiTietDonHang.objects.create(
    don_hang=order1,
    san_pham=sp_objects['MP-S96-001'],
    so_luong=1,
    don_gia=11645000
)

order2 = DonDatHang.objects.create(
    ma_don_hang='DH20260122002',
    ho_ten='An Nguyễn Văn',
    so_dien_thoai='0349434950',
    dia_chi='68-Dương Khuê, Thành phố Đà Nẵng, Quận Sơn Trà, Phường Phước Mỹ',
    trang_thai='giao_hang_thanh_cong',
    hinh_thuc_thanh_toan='tien_mat',
    trang_thai_thanh_toan='da_thanh_toan',
    tien_coc=0,
    nhan_vien_phu_trach='Nguyễn Văn A',
)

ChiTietDonHang.objects.create(
    don_hang=order2,
    san_pham=sp_objects['KG-A20-003'],
    so_luong=1,
    don_gia=5211000
)

order3 = DonDatHang.objects.create(
    ma_don_hang='DH20260315003',
    ho_ten='Trần Thị Bình',
    so_dien_thoai='0901234567',
    dia_chi='123 Lê Lợi, Quận 1, TP. Hồ Chí Minh',
    trang_thai='da_xac_nhan',
    hinh_thuc_thanh_toan='chuyen_khoan',
    trang_thai_thanh_toan='da_thanh_toan',
    tien_coc=5000000,
    nhan_vien_phu_trach='Lê Minh B',
)

ChiTietDonHang.objects.create(
    don_hang=order3,
    san_pham=sp_objects['MP-P89-010'],
    so_luong=1,
    don_gia=15500000
)

ChiTietDonHang.objects.create(
    don_hang=order3,
    san_pham=sp_objects['FLT-7S-004'],
    so_luong=2,
    don_gia=450000
)

order4 = DonDatHang.objects.create(
    ma_don_hang='DH20260320004',
    ho_ten='Phạm Văn Cường',
    so_dien_thoai='0987654321',
    dia_chi='456 Trần Phú, Quận Hải Châu, Đà Nẵng',
    trang_thai='dang_giao_hang',
    hinh_thuc_thanh_toan='tien_mat',
    trang_thai_thanh_toan='chua_thanh_toan',
    tien_coc=2000000,
    nhan_vien_phu_trach='Nguyễn Văn A',
)

ChiTietDonHang.objects.create(
    don_hang=order4,
    san_pham=sp_objects['GM-A01-018'],
    so_luong=1,
    don_gia=6800000
)

print("\n=== Sample data created successfully! ===")
print(f"Categories: {DanhMuc.objects.count()}")
print(f"Products: {SanPham.objects.count()}")
print(f"Orders: {DonDatHang.objects.count()}")
print(f"Order items: {ChiTietDonHang.objects.count()}")
