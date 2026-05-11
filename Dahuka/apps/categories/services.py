from typing import Dict, Any, Tuple, Optional
from django.db import transaction
from .models import Category
from .forms import CategoryForm

# ==============================================================================
# SERVICE LAYER: XỬ LÝ LOGIC NGHIỆP VỤ (Business Logic Layer)
# ==============================================================================
# Theo kiến trúc Service Layer, Views chỉ làm nhiệm vụ điều hướng (nhận Request, 
# gọi Service, trả về Response). Toàn bộ logic xử lý dữ liệu phức tạp sẽ nằm 
# tại đây để dễ dàng tái sử dụng và viết Unit Test.

class CategoryService:
    """
    Tập hợp các phương thức xử lý các thao tác chính với Danh mục sản phẩm.
    Đảm bảo tính nhất quán và an toàn dữ liệu thông qua các giao dịch (Transactions).
    """

    @staticmethod
    @transaction.atomic
    def create_category(data: Dict[str, Any], files: Any = None) -> Tuple[bool, Optional[Category], Dict[str, Any]]:
        """
        Thực hiện quy trình thêm mới một danh mục sản phẩm vào hệ thống.
        
        Args:
            data (Dict): Dữ liệu văn bản từ yêu cầu người dùng (request.POST).
            files (Any): Dữ liệu tệp tin hình ảnh đính kèm (request.FILES).
            
        Returns:
            Tuple: Trả về bộ 3 giá trị (Thành công hay không?, Đối tượng đã tạo, Danh sách lỗi nếu có).
        """
        # 1. Khởi tạo Form và thực hiện kiểm tra tính hợp lệ (Validation)
        form = CategoryForm(data, files)
        
        if form.is_valid():
            # 2. Nếu dữ liệu hợp lệ, tiến hành lưu vào Database
            category = form.save()
            return True, category, {}
            
        # 3. Trả về lỗi của Form nếu có (Ví dụ: Trùng tên, dữ liệu không đúng định dạng...)
        return False, None, form.errors

    @staticmethod
    @transaction.atomic
    def update_category(category: Category, data: Dict[str, Any], files: Any = None) -> Tuple[bool, Optional[Category], Dict[str, Any]]:
        """
        Thực hiện quy trình cập nhật thông tin cho một danh mục đang tồn tại.
        
        Args:
            category (Category): Đối tượng danh mục cần được chỉnh sửa.
            data, files: Dữ liệu mới cần cập nhật.
        """
        # 1. Khởi tạo Form với tham số instance=category để Django hiểu là thao tác CẬP NHẬT (Update)
        form = CategoryForm(data, files, instance=category)
        
        if form.is_valid():
            # 2. Lưu các thay đổi mới nhất vào Database
            category = form.save()
            return True, category, {}
            
        return False, None, form.errors

    @staticmethod
    @transaction.atomic
    def delete_category(category: Category) -> Tuple[bool, str]:
        """
        Thực hiện xóa vĩnh viễn một danh mục khỏi hệ thống.
        
        LƯU Ý CẨN TRỌNG: Do thiết lập liên kết dữ liệu (Foreign Key), việc xóa một 
        danh mục có thể dẫn đến việc xóa hàng loạt sản phẩm liên quan nếu không xử lý kỹ.
        """
        # Lưu lại tên danh mục trước khi xóa để hiển thị thông báo phản hồi cho người dùng
        name = category.name
        
        # Thực thi lệnh xóa khỏi Database
        category.delete()
        
        return True, name
