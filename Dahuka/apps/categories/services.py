from typing import Dict, Any, Tuple, Optional
from django.db import transaction
from .models import Category
from .forms import CategoryForm

class CategoryService:
    @staticmethod
    @transaction.atomic
    def create_category(data: Dict[str, Any], files: Any = None) -> Tuple[bool, Optional[Category], Dict[str, Any]]:
        """
        Validates and creates a new category using CategoryForm.
        """
        form = CategoryForm(data, files)
        if form.is_valid():
            category = form.save()
            return True, category, {}
        return False, None, form.errors

    @staticmethod
    @transaction.atomic
    def update_category(category: Category, data: Dict[str, Any], files: Any = None) -> Tuple[bool, Optional[Category], Dict[str, Any]]:
        """
        Validates and updates an existing category instance using CategoryForm.
        """
        form = CategoryForm(data, files, instance=category)
        if form.is_valid():
            category = form.save()
            return True, category, {}
        return False, None, form.errors

    @staticmethod
    @transaction.atomic
    def delete_category(category: Category) -> Tuple[bool, str]:
        """
        Deletes a category and returns its name for feedback.
        """
        name = category.name
        category.delete()
        return True, name
