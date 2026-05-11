from typing import Any, Dict, List
from django.db import transaction
from .models import Product, ProductImage


# Service layer: Toàn bộ business logic của app products
class ProductsService:

    # Định dạng danh sách sản phẩm thành JSON để trả về cho AJAX
    # Dùng khi người dùng click vào hàng danh mục → hiển thị sản phẩm bên trong
    @staticmethod
    def format_products_for_dropdown(
        category: Any, query: str = ""
    ) -> List[Dict[str, Any]]:
        products_qs = Product.objects.filter(category=category)
        if query:
            products_qs = products_qs.filter(name__icontains=query)

        products = []
        for p in products_qs:
            products.append(
                {
                    "id": p.id,
                    "name": p.name,
                    "price": float(p.price),
                    "stock": p.stock,
                    "is_active": p.is_active,
                    "stock_status": p.stock_status,  # 'het_hang' | 'thap' | 'day_du'
                    "stock_status_display": p.stock_status_display,
                    "category": p.category.name,
                }
            )
        return products

    # Xử lý upload nhiều ảnh gallery khi admin thêm/sửa sản phẩm
    # Mỗi ảnh tải lên → tạo 1 bản ghi ProductImage liên kết với sản phẩm
    @staticmethod
    def handle_product_images(product: Product, files: Any) -> None:
        # getlist: Lấy tất cả các tệp tin từ ô input HTML (multiple) thay vì chỉ lấy 1 tệp.
        gallery_images = files.getlist("gallery_images")

        if not gallery_images:
            return

        # transaction.atomic(): Đảm bảo tính nhất quán (Atomicity).
        with transaction.atomic():
            for img in gallery_images:
                ProductImage.objects.create(product=product, image_url=img)

    # Bật/tắt hiển thị sản phẩm trên website
    # is_visible=True → sản phẩm đang kinh doanh; False → ẩn khỏi khách hàng
    @staticmethod
    def toggle_visibility(product: Product, is_visible: bool) -> bool:
        product.is_active = is_visible
        product.save()
        return product.is_active
