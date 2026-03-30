import os

BASE_DIR = r"d:\File Code\PyCharm\Project_LTW_Nhom1\Dahuka"
APPS_DIR = os.path.join(BASE_DIR, "apps")

# Generate services.py for all apps
for app in os.listdir(APPS_DIR):
    app_path = os.path.join(APPS_DIR, app)
    if os.path.isdir(app_path):
        services_path = os.path.join(app_path, "services.py")
        if not os.path.exists(services_path):
            with open(services_path, "w", encoding="utf-8") as f:
                f.write(f"\"\"\"\nServices for {app} module.\nPut business logic here to keep views lean.\n\"\"\"\n\nclass {app.capitalize()}Service:\n    pass\n")
            print(f"Created {services_path}")
