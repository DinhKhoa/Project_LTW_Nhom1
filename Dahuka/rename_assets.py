import os
import shutil

BASE_DIR = r"d:\File Code\PyCharm\Project_LTW_Nhom1\Dahuka"
APPS_DIR = os.path.join(BASE_DIR, "apps")

mapping = {
    "account": "account",
    "quanlysanpham": "products",
    "quanlydondathang": "orders",
    "quanlygiohang": "cart",
    "quanlykhuyenmai": "promotions",
    "quanlydanhmuc": "categories",
    "diembanbaohanh": "warranty",
    "quanlynhiemvu": "tasks",
    "trangchu": "core",
}

def rename_subfolders(base_path):
    if not os.path.exists(base_path):
        return
    for old, new in mapping.items():
        if old == new: continue
        old_path = os.path.join(base_path, old)
        new_path = os.path.join(base_path, new)
        if os.path.exists(old_path) and os.path.isdir(old_path):
            os.rename(old_path, new_path)
            print(f"Renamed {old_path} to {new_path}")

# Rename inside project root templates/ and static/
rename_subfolders(os.path.join(BASE_DIR, "templates"))
rename_subfolders(os.path.join(BASE_DIR, "static"))

# Rename inside each app's templates/ and static/
for app in os.listdir(APPS_DIR):
    app_path = os.path.join(APPS_DIR, app)
    if os.path.isdir(app_path):
        rename_subfolders(os.path.join(app_path, "templates"))
        rename_subfolders(os.path.join(app_path, "static"))

print("Done renaming template and static subfolders.")
