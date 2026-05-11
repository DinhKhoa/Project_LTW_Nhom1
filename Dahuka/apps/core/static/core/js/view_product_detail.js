/**
 * Xử lý thay đổi ảnh chính khi người dùng click vào ảnh thu nhỏ (Thumbnail)
 * @param {HTMLElement} thumbElement - Phần tử chứa ảnh thu nhỏ được click
 */
function updateMainImage(thumbElement) {
    const img = thumbElement.querySelector('img');
    const mainImg = document.getElementById('mainImg');
    if (img && mainImg) {
        // Cập nhật nguồn ảnh (src) của ảnh chính bằng ảnh vừa click
        mainImg.src = img.src;
        
        // Cập nhật trạng thái 'active' (đường viền xanh) cho ảnh thu nhỏ đang chọn
        document.querySelectorAll('.thumb-box').forEach(el => el.classList.remove('active'));
        thumbElement.classList.add('active');
    }
}

/**
 * Điều khiển chuyển đổi giữa các Tab nội dung (Mô tả, Thông số, Đánh giá)
 * @param {HTMLElement} btn - Nút tab vừa được click
 * @param {string} tabId - ID của khối nội dung tương ứng cần hiển thị
 */
function openTab(btn, tabId) {
    // 1. Cập nhật trạng thái Active cho các nút bấm (hỗ trợ cả class legacy và minimal)
    document.querySelectorAll('.tab-btn, .tab-btn-minimal').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // 2. Ẩn tất cả các nội dung tab cũ và hiển thị nội dung tab được chọn
    document.querySelectorAll('.tab-content, .tab-content-minimal').forEach(c => c.classList.remove('active'));
    const target = document.getElementById(tabId);
    if (target) {
        target.classList.add('active');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Có thể bổ sung logic khởi tạo hiệu ứng Zoom ảnh tại đây nếu cần
});