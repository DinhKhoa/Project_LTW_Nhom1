// Biến lưu trữ vị trí sản phẩm đang muốn thay thế (-1 nghĩa là thêm mới)
let currentReplaceIndex = -1;
// Danh sách các ID sản phẩm đang hiển thị trên bảng so sánh hiện tại
let currentProductIds = [];

document.addEventListener('DOMContentLoaded', function() {
    // Lấy dữ liệu ID từ thẻ JSON script được Render từ Django
    const idsData = document.getElementById('current-product-ids');
    if (idsData) {
        currentProductIds = JSON.parse(idsData.textContent).map(id => id.toString());
    }

    // Đóng Modal khi người dùng nhấn phím ESC
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeSelectionModal();
    });
});

/** Mở cửa sổ chọn sản phẩm để thêm vào bảng so sánh */
function openSelectionModal(index = -1) {
    currentReplaceIndex = index;
    const modal = document.getElementById('selectionModal');
    if (modal) modal.classList.add('active');
}

/** Đóng cửa sổ chọn sản phẩm */
function closeSelectionModal() {
    const modal = document.getElementById('selectionModal');
    if (modal) modal.classList.remove('active');
}

/** 
 * Xử lý khi người dùng chọn một sản phẩm từ Modal 
 * @param {string} id - ID của sản phẩm được chọn
 */
function selectProduct(id) {
    // Kiểm tra xem sản phẩm đã có trong bảng so sánh chưa
    if (currentProductIds.includes(id)) {
        window.showToast('Sản phẩm này đã có trong danh sách so sánh!', 'warning');
        return;
    }

    let newIds = [...currentProductIds];
    // Nếu đang ở chế độ thay thế (nhấn nút "Thay đổi" trên cột), thực hiện gán đè ID
    if (currentReplaceIndex >= 0) {
        newIds[currentReplaceIndex] = id;
    } else {
        // Nếu nhấn nút "Thêm" trống, thực hiện đẩy thêm vào mảng
        newIds.push(id);
    }

    // Cập nhật lại URL và tải lại trang để Server render bảng mới
    updateUrlAndReload(newIds);
}

/** Xóa một sản phẩm khỏi danh sách so sánh */
function removeItem(id) {
    const newIds = currentProductIds.filter(i => i !== id);
    updateUrlAndReload(newIds);
}

/**
 * Cập nhật tham số trên URL (?id=...&id=...) và tải lại trang
 * Đồng thời đồng bộ hóa với LocalStorage để thanh Compare Bar toàn cục được cập nhật theo.
 */
function updateUrlAndReload(ids) {
    // 1. Đồng bộ hóa với thanh so sánh toàn cục (localStorage)
    let compareItems = JSON.parse(localStorage.getItem('compareItems') || '[]');
    // Lọc bỏ những id không còn nằm trong danh sách so sánh mới
    compareItems = compareItems.filter(item => ids.includes(item.id.toString()));
    localStorage.setItem('compareItems', JSON.stringify(compareItems));
    
    // 2. Lưu trữ danh sách ID thô vào LocalStorage
    localStorage.setItem('compareIds', JSON.stringify(ids));
    
    // 3. Tạo chuỗi truy vấn (Query String) mới cho URL
    const params = new URLSearchParams();
    ids.forEach(id => params.append('id', id));
    
    // 4. Chuyển hướng trang (Reload) với các tham số mới
    window.location.href = window.location.pathname + '?' + params.toString();
}

// Xuất các hàm ra đối tượng window để các thuộc tính onclick trong HTML có thể gọi được
window.openSelectionModal = openSelectionModal;
window.closeSelectionModal = closeSelectionModal;
window.selectProduct = selectProduct;
window.removeItem = removeItem;
