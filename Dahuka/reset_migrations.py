import os
import shutil

BASE_DIR = r"d:\File Code\PyCharm\Project_LTW_Nhom1\Dahuka"
APPS_DIR = os.path.join(BASE_DIR, "apps")

# Delete db.sqlite3
db_path = os.path.join(BASE_DIR, "db.sqlite3")
if os.path.exists(db_path):
    os.remove(db_path)
    print("Deleted db.sqlite3")

# Delete migration files
for app_name in os.listdir(APPS_DIR):
    app_dir = os.path.join(APPS_DIR, app_name)
    if os.path.isdir(app_dir):
        migrations_dir = os.path.join(app_dir, "migrations")
        if os.path.exists(migrations_dir) and os.path.isdir(migrations_dir):
            for filename in os.listdir(migrations_dir):
                if filename != "__init__.py" and filename.endswith(".py"):
                    file_path = os.path.join(migrations_dir, filename)
                    os.remove(file_path)
            # Remove custom pycache for migrations
            pycache = os.path.join(migrations_dir, "__pycache__")
            if os.path.exists(pycache):
                shutil.rmtree(pycache)
            print(f"Cleared migrations for {app_name}")
