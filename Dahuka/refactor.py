import os
import shutil

BASE_DIR = r"d:\File Code\PyCharm\Project_LTW_Nhom1\Dahuka"
APPS_DIR = os.path.join(BASE_DIR, "apps")

mapping = {
    "apps.account": "apps.account",
    "apps.products": "products",
    "apps.orders": "orders",
    "apps.cart": "cart",
    "apps.promotions": "promotions",
    "apps.categories": "categories",
    "apps.warranty": "warranty",
    "apps.tasks": "tasks",
    "apps.core": "core",
}

if not os.path.exists(APPS_DIR):
    os.makedirs(APPS_DIR)

# 1. Move folders
for old, new in mapping.items():
    old_path = os.path.join(BASE_DIR, old)
    new_path = os.path.join(APPS_DIR, new)
    if os.path.exists(old_path) and os.path.isdir(old_path):
        os.rename(old_path, new_path)
        print(f"Moved {old} to apps/{new}")

# 2. Update files
for root, dirs, files in os.walk(BASE_DIR):
    # skip venv, .idea, __pycache__, etc
    if any(ignore in root for ignore in [".git", ".idea", "__pycache__", "venv"]):
        continue

    for file in files:
        if file.endswith((".py", ".html")):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    content = f.read()
                except UnicodeDecodeError:
                    continue
            
            new_content = content
            for old, new in mapping.items():
                if file.endswith(".py"):
                    # imports
                    new_content = new_content.replace(f"from {old}", f"from apps.{new}")
                    new_content = new_content.replace(f"import {old}", f"import apps.{new}")
                    new_content = new_content.replace(f"'{old}'", f"'apps.{new}'")
                    new_content = new_content.replace(f"\"{old}\"", f"\"apps.{new}\"")
                    new_content = new_content.replace(f"'{old}.", f"'apps.{new}.")
                    new_content = new_content.replace(f"\"{old}.", f"\"apps.{new}.")
                    
                    # url namespaces
                    new_content = new_content.replace(f"namespace='{old}'", f"namespace='{new}'")
                    new_content = new_content.replace(f"namespace=\"{old}\"", f"namespace=\"{new}\"")
                    new_content = new_content.replace(f"'{old}:", f"'{new}:")
                    new_content = new_content.replace(f"\"{old}:", f"\"{new}:")

                    # template path
                    new_content = new_content.replace(f"'{old}/", f"'{new}/")
                    new_content = new_content.replace(f"\"{old}/", f"\"{new}/")

                elif file.endswith(".html"):
                    # url tagging
                    new_content = new_content.replace(f"'{old}:", f"'{new}:")
                    new_content = new_content.replace(f"\"{old}:", f"\"{new}:")
                    new_content = new_content.replace(f" {old}:", f" {new}:")

            if content != new_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated {file_path}")

print("Done refactoring directories and basic imports.")
