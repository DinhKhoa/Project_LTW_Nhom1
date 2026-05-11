document.addEventListener('DOMContentLoaded', function() {

    // --- PHẦN 1: LOGIC ĐÓNG/MỞ BẢNG CON (Expandable Row Logic) ---
    // Tìm tất cả các dòng danh mục chính (dm-row) để gán sự kiện click
    document.querySelectorAll('.dm-row').forEach(function(row) {
        row.addEventListener('click', function() {
            // 1. Lấy ID danh mục từ thuộc tính data-dm-id
            var dmId = this.getAttribute('data-dm-id');
            // 2. Tìm dòng bảng con tương ứng dựa trên ID (Ví dụ: detail-5)
            var detailRow = document.getElementById('detail-' + dmId);

            // Kiểm tra: Nếu dòng đang ẩn thì tiến hành hiện và load dữ liệu
            if (detailRow.style.display === 'none' || detailRow.style.display === '') {
                // Hiển thị dòng bảng con
                detailRow.style.display = 'table-row';
                this.classList.add('expanded'); // Thêm class để xoay mũi tên hoặc đổi màu dòng

                // --- PHẦN 2: GỌI AJAX ĐỂ LẤY SẢN PHẨM (Fetch Products) ---
                var tbody = detailRow.querySelector('.product-tbody');

                console.log('Đang lấy sản phẩm cho danh mục ID:', dmId);
                
                // Gọi API của Django: URL này trả về dữ liệu JSON của các sản phẩm
                fetch('/categories/products/' + dmId + '/')
                    .then(response => {
                        if (!response.ok) throw new Error('Lỗi mạng hoặc server.');
                        return response.json(); // Chuyển đổi phản hồi sang dạng đối tượng JS
                    })
                    .then(data => {
                        // Xóa sạch nội dung cũ (dòng chữ "Đang tải...") trong tbody
                        tbody.innerHTML = '';
                        
                        // Kiểm tra nếu danh mục không có sản phẩm nào
                        if (!data.products || data.products.length === 0) {
                            tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4">Chưa có sản phẩm nào trong danh mục này.</td></tr>';
                            return;
                        }

                        // Duyệt qua từng sản phẩm (p) trong danh sách nhận được
                        data.products.forEach(p => {
                            // Xử lý các biến hiển thị (màu sắc, nhãn trạng thái)
                            const statusType = p.stock_status || 'day_du'; 
                            const statusText = p.stock_status_display || 'Đầy đủ';
                            const badgeClass = 'badge-' + statusType.replace('_', '');
                            const rowClass = (statusType === 'het_hang') ? 'row-hethang' : (statusType === 'thap' ? 'row-thap' : 'row-daydu');
                            
                            const toggleClass = p.is_active ? 'active-toggle' : '';
                            const toggleText = p.is_active ? 'Hiển thị' : 'Ẩn';
                            
                            // Định dạng giá tiền sang chuẩn Việt Nam (1.000.000 đ)
                            const formattedPrice = (p.price || 0).toLocaleString('vi-VN');
                            
                            // Xử lý hiển thị số lượng tồn kho (vô cực nếu số lượng quá lớn)
                            let stockDisplay = p.stock;
                            if (parseInt(p.stock) >= 999) stockDisplay = '∞';

                            // Tạo một dòng mới (tr) cho bảng sản phẩm
                            const tr = document.createElement('tr');
                            tr.className = rowClass;
                            
                            // Khi click vào dòng sản phẩm (trừ nút switch) -> Chuyển sang trang chi tiết SP
                            tr.onclick = (e) => {
                                if (!e.target.closest('.switch-wrapper')) {
                                    window.location.href = `/products/${p.id}/`;
                                }
                            };
                            
                            // Xây dựng nội dung HTML cho dòng sản phẩm (Bơm dữ liệu vào đây)
                            tr.innerHTML = `
                                <td class="text-center">${p.id || ''}</td>
                                <td class="p-name">${p.name || ''}</td>
                                <td class="p-price text-center brand-green-text font-weight-bold">${formattedPrice} đ</td>
                                <td class="p-stock text-center">${stockDisplay}</td>
                                <td class="text-center">
                                    <div class="stock-badge ${badgeClass} mx-auto">
                                        <span class="dot"></span> ${statusText}
                                    </div>
                                </td>
                                <td class="text-center">
                                    <div class="switch-wrapper ${toggleClass} mx-auto" 
                                         onclick="toggleVisibility(event, ${p.id}, this)">
                                        <div class="toggle-slider"></div>
                                        <span class="toggle-label">${toggleText}</span>
                                    </div>
                                </td>
                            `;
                            // Thêm dòng vừa tạo vào thân bảng (tbody)
                            tbody.appendChild(tr);
                        });
                    })
                    .catch(error => {
                        console.error('Fetch error:', error);
                        tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-danger">Lỗi khi tải dữ liệu sản phẩm.</td></tr>';
                    });
            } else {
                // Nếu đang mở mà click lại -> Đóng bảng con
                detailRow.style.display = 'none';
                this.classList.remove('expanded');
            }
        });
    });
});

/* ===== PHẦN 3: XỬ LÝ ẨN/HIỆN SẢN PHẨM (AJAX) ===== */
// Hàm này được gọi khi bạn gạt nút công tắc trên dòng sản phẩm
window.toggleVisibility = function(event, productId, element) {
    event.stopPropagation(); // Ngăn sự kiện click lan ra ngoài dòng tr

    const isVisible = !element.classList.contains('active-toggle');
    const label = element.querySelector('.toggle-label');

    // Gửi yêu cầu thay đổi trạng thái ẩn/hiện đến server
    fetch(`/products/toggle-visibility/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Gửi Token bảo mật
        },
        body: JSON.stringify({ is_visible: isVisible })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Cập nhật giao diện nút gạt ngay lập tức
            if (data.is_active) {
                element.classList.add('active-toggle');
                label.textContent = 'Hiển thị';
            } else {
                element.classList.remove('active-toggle');
                label.textContent = 'Ẩn';
            }
        } else {
            window.showToast('Lỗi: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        window.showToast('Có lỗi xảy ra khi cập nhật trạng thái.', 'error');
    });
};

/**
 * Hàm lấy Cookie (Dùng để lấy CSRF Token phục vụ các yêu cầu POST của Django)
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/* ===== PHẦN 4: ĐIỀU KHIỂN CÁC CỬA SỔ POPUP (Modals) ===== */

// Hàm Mở Modal Thêm hoặc Sửa danh mục
window.openCategoryModal = function(mode, id, ten) {
    var modal = document.getElementById('categoryModal');
    var form = document.getElementById('categoryForm');
    var title = document.getElementById('modalTitle');
    var tenInput = document.getElementById('category_name');
    var submitBtn = document.getElementById('submitBtn');

    if (mode === 'edit') {
        // Chế độ Sửa: Đổi tiêu đề và hành động của Form, điền tên cũ vào ô nhập
        title.textContent = 'CHỈNH SỬA DANH MỤC';
        form.action = '/categories/edit/' + id + '/';
        tenInput.value = ten;
        submitBtn.innerHTML = 'Lưu thay đổi';
    } else {
        // Chế độ Thêm: Đặt lại Form trống
        title.textContent = 'THÊM DANH MỤC MỚI';
        form.action = '/categories/add/';
        tenInput.value = '';
        submitBtn.innerHTML = 'Thêm mới';
    }

    modal.classList.add('show');
};

// Đóng Modal danh mục
window.closeCategoryModal = function() {
    document.getElementById('categoryModal').classList.remove('show');
};

// Mở Modal xác nhận xóa
window.openDeleteModal = function(id, name) {
    var modal = document.getElementById('deleteModal');
    var form = document.getElementById('deleteForm');
    var nameSpan = document.getElementById('deleteTargetName');

    // Gán ID danh mục cần xóa vào địa chỉ URL của Form xóa
    form.action = '/categories/delete/' + id + '/';
    nameSpan.textContent = name;
    modal.classList.add('show');
};

// Đóng Modal xóa
window.closeDeleteModal = function() {
    document.getElementById('deleteModal').classList.remove('show');
};

// Tự động đóng Modals nếu người dùng click ra ngoài vùng Popup
window.onclick = function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        closeCategoryModal();
        closeDeleteModal();
    }
};
