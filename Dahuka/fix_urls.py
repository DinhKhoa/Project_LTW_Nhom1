import os
import re

BASE_DIR = r"d:\File Code\PyCharm\Project_LTW_Nhom1\Dahuka"
APPS_DIR = os.path.join(BASE_DIR, "apps")

for app in os.listdir(APPS_DIR):
    urls_path = os.path.join(APPS_DIR, app, "urls.py")
    if os.path.exists(urls_path):
        with open(urls_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # fix app_name
        content = re.sub(rf"app_name\s*=\s*['\"]apps\.({app})['\"]", rf"app_name = '\1'", content)
        
        # fix name='apps.core' -> name='trangchu' inside core
        if app == 'core':
            content = content.replace("name='apps.core'", "name='trangchu'")
            content = content.replace("name=\"apps.core\"", "name='trangchu'")
        
        # Fix any other name='apps.xxxx' to its original name if necessary. 
        # For simplicity, if we find name='apps.products', usually it shouldn't have been renamed from 'danh_sach' to 'apps.products'.
        # Wait! The original 'trangchu' view was named 'trangchu', so old code was: name='trangchu'
        # old script replaced 'trangchu' with 'apps.core'. Let's revert name='apps.xyz' back to 'xyz'
        # Or better exactly match `name='apps.something'`
        content = re.sub(r"name=['\"]apps\.([^'\"]+)['\"]", r"name='\1'", content)
        
        with open(urls_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed {urls_path}")
