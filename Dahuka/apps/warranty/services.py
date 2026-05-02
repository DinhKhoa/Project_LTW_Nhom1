from django.http import QueryDict
from django.utils.datastructures import MultiValueDict
from .models import WarrantyPageSettings
from .selectors import get_warranty_settings

class WarrantyService:
    @staticmethod
    def update_settings(files: MultiValueDict) -> WarrantyPageSettings:
        settings = get_warranty_settings()
        
        if 'image_one' in files:
            settings.image_one = files['image_one']
        if 'image_two' in files:
            settings.image_two = files['image_two']
            
        settings.save()
        return settings
