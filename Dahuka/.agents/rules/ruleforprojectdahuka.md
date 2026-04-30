---
trigger: always_on
---

# Quy tắc Phát triển Dự án Dahuka

## I. Quy tắc về Tra cứu & Cấu trúc (BẮT BUỘC)

* **Ưu tiên STRUCTURE.md:** "Trước khi thực hiện bất kỳ thao tác tìm kiếm file nào, Agent **PHẢI** đọc tệp `document/STRUCTURE.md` đầu tiên để hiểu rõ sơ đồ phân cấp và vị trí của các tệp tin trong dự án. Điều này giúp tránh việc sử dụng các lệnh tìm kiếm mù quáng gây lãng phí tài nguyên và thời gian."

## II. Quy tắc về Chất lượng Code & Quy trình

### 1. Quy tắc về Chất lượng Code (Django/Python)

* **Type Hinting:** "Mọi hàm Python mới phải có type hints để dễ dàng kiểm soát dữ liệu."
* **Security First:** "Mọi View mới phải kiểm tra quyền truy cập (Decorator `@login_required` hoặc `LoginRequiredMixin`) trừ khi được chỉ định là công khai."
* **DRY (Don't Repeat Yourself):** "Nếu thấy logic lặp lại quá 2 lần trong `views.py` hoặc `models.py`, hãy gợi ý tách ra thành một hàm helper hoặc utility."

### 2. Quy tắc về Giao diện (UI/UX)

* **Design Tokens:** "Luôn sử dụng hệ thống biến CSS (CSS Variables) cho màu sắc và khoảng cách để dễ dàng thay đổi theme sau này, thay vì dùng mã màu cứng (hard-coded)."
* **Responsive:** "Mọi thành phần UI mới phải đảm bảo hiển thị tốt trên thiết bị di động trước khi hoàn thành."
* **Loading States:** "Khi thực hiện các tác vụ bất đồng bộ (AJAX/Fetch), luôn phải có hiệu ứng loading hoặc vô hiệu hóa nút bấm để tránh người dùng nhấn nhiều lần."

### 3. Quy tắc về Quy trình & Git

* **Commit Messages:** "Gợi ý tin nhắn commit theo chuẩn [Conventional Commits](https://www.conventionalcommits.org/) (ví dụ: `feat: add quantity stepper to cart`)."
* **Auto-Testing:** "Trước khi kết thúc một tính năng phức tạp, hãy nhắc tôi viết hoặc chạy test case cho tính năng đó."

### 4. Quy tắc về Tài liệu (Documentation)

* **Docstrings:** "Tự động viết docstring cho các hàm và lớp mới theo chuẩn Google hoặc NumPy."
* **README Update:** "Nếu có thay đổi về cài đặt hoặc thư viện mới (requirements.txt), hãy nhắc tôi cập nhật file README hoặc hướng dẫn cài đặt."

---

## II. Quy tắc Clean Architecture

### 1. Quy tắc Service Layer (Tách biệt Business Logic)

* **Nội dung:** "Tuyệt đối không viết logic nghiệp vụ phức tạp (tính toán, xử lý dữ liệu, gọi API bên thứ ba) trực tiếp trong `views.py`. Mọi logic này phải được đưa vào một file `services.py` trong mỗi app."
* **Mục tiêu:** Views chỉ làm nhiệm vụ điều hướng (nhận request, gọi service, trả về response). Bạn có thể tái sử dụng Service ở nhiều nơi (View, Command, Celery task) mà không phải viết lại.

### 2. Quy tắc Fat Models, Skinny Views (hoặc Service-centric)

* **Nội dung:** "Nếu một đoạn logic liên quan chặt chẽ đến dữ liệu của Model, hãy đặt nó vào Model method. Nếu logic liên quan đến nhiều Model hoặc quy trình phức tạp, hãy dùng Service. Views phải 'gầy' (Skinny) nhất có thể."
* **Mục tiêu:** Giảm sự phụ thuộc lẫn nhau và làm rõ nơi quản lý dữ liệu.

### 3. Quy tắc "No Logic in Templates"

* **Nội dung:** "Templates chỉ dùng để hiển thị. Cấm thực hiện các truy vấn database phức tạp hoặc logic tính toán nặng trong Template (ví dụ: `{% if order.items.all.count > 5 %}`). Mọi dữ liệu cần thiết phải được chuẩn bị sẵn từ View hoặc Model property."
* **Mục tiêu:** Giữ giao diện sạch sẽ và tránh các lỗi hiệu năng (như N+1 query) khó kiểm soát.

### 4. Quy tắc Selectors (Tách biệt logic truy vấn)

* **Nội dung:** "Các truy vấn phức tạp hoặc được dùng lại nhiều lần (như lọc sản phẩm đang giảm giá, lấy giỏ hàng của user hiện tại) nên được tách ra thành các hàm trong file `selectors.py`."
* **Mục tiêu:** Tránh việc viết đi viết lại các câu lệnh `.filter().exclude().annotate()` ở khắp nơi.

### 5. Quy tắc Single Responsibility (Đơn nhiệm)

* **Nội dung:** "Mỗi hàm hoặc class chỉ nên làm một việc duy nhất. Nếu một View đang vừa xử lý form, vừa gửi email, vừa cập nhật kho hàng, hãy nhắc tôi tách chúng ra thành các Service nhỏ hơn."
* **Mục tiêu:** Dễ viết unit test và dễ đọc code.

---

## III. Kiến thức Django Chuyên sâu (Advanced Best Practices)

### 1. Kiến trúc & URL (Chapter 1, 3)

* **Standalone Apps:** Chia nhỏ logic thành các ứng dụng độc lập để tăng khả năng tái sử dụng.
* **Modern URLs:** Luôn sử dụng cú pháp `path()` thay cho regex cũ.
* **Namespace Strictly:** Tuyệt đối sử dụng `app_name:path_name` khi gọi URL (ví dụ: `{% url 'account:profile' %}`) để tránh xung đột tên giữa các app.

### 2. Models, Migrations & Database (Chapter 2, 9, 10, 15)

* **ORM Optimization:** Ưu tiên sử dụng `bulk_create()` và `bulk_update()`. Sử dụng `Q objects` cho các logic truy vấn phức tạp (OR, NOT).
* **N+1 Query:** Luôn sử dụng `select_related()` (ForeignKey/OneToOne) và `prefetch_related()` (ManyToMany/Reverse FK). Tích hợp `django-debug-toolbar` để kiểm tra.
* **Custom User:** Luôn kế thừa từ `AbstractUser` ngay từ đầu để đảm bảo tính linh hoạt.
* **Signal Patterns:** Sử dụng `post_save` trên User model để tự động hóa các tác vụ liên quan (ví dụ: tự động tạo `Customer` profile).

### 3. Forms & Bảo mật (Chapter 6, 7)

* **ModelForm Security:** Luôn định nghĩa rõ ràng danh sách `fields` trong lớp Meta. **CẤM** sử dụng `fields = '__all__'` để tránh lỗ hổng Mass Assignment.
* **Validation:** Sử dụng phương thức `clean()` cho logic liên trường (cross-field) và tạo Custom Validators khi cần tái sử dụng.

### 4. Admin & Giao diện quản trị (Chapter 4, 10)

* **Decorator usage:** Sử dụng `@admin.register(Model)`.
* **Efficiency:** Tối ưu hóa bằng `list_display`, `list_filter`, và `search_fields`.
* **Professional UI:** Sử dụng `InlineModelAdmin` (Tabular/Stacked) cho các dữ liệu liên quan và tạo `Admin Actions` cho các tác vụ hàng loạt.

### 5. Files, Media & Static (Chapter 5, 8, 13)

* **Static Management:** Sử dụng `WhiteNoise` và `ManifestStaticFilesStorage` để tối ưu hóa caching (hashing) ở môi trường production.
* **Media Isolation:** Tuyệt đối không để Django phục vụ file media ở production (nên dùng Nginx/S3). Sử dụng hàm cụ thể để định nghĩa `upload_to` nhằm tổ chức file khoa học.
* **Large Exports:** Sử dụng `StreamingHttpResponse` khi xuất file CSV/PDF dung lượng lớn để tiết kiệm bộ nhớ.

### 6. Templates & Frontend (Chapter 11, 16)

* **CBV usage:** Ưu tiên `ListView`, `DetailView` cho các tác vụ CRUD tiêu chuẩn.
* **Inclusion Tags:** Các thành phần UI lặp lại (Navbar, Sidebar, Footer) phải được tách thành `inclusion_tags`.
* **API-First:** Khi tích hợp Frontend hiện đại (Vue/React), hãy sử dụng kiến trúc tách biệt hoàn toàn (Decoupled Architecture) và dùng JWT cho xác thực.

### 7. REST API (Chapter 12)

* **DRF Best Practices:** Sử dụng `Serializers` để kiểm soát dữ liệu đầu ra và `ViewSets/Routers` để chuẩn hóa cấu trúc URI.

### 8. Testing & Reliability (Chapter 14)

* **Auto-Testing:** Sử dụng `TestCase` để đảm bảo cô lập database.
* **Mocking Data:** Sử dụng `Factory Boy` hoặc `Faker` để tạo dữ liệu test thay vì viết cứng.