/**
 * Thay đổi ảnh chính khi di chuột qua/nhấn vào ảnh nhỏ (Thumbnails)
 */
function changeImage(themeName, thumbElement) {
    const mainImg = document.getElementById('main-product-img'); // Vùng hiển thị ảnh lớn
    const thumbs = document.querySelectorAll('.thumb'); // Danh sách các ảnh nhỏ

    // Tạo hiệu ứng mờ dần khi đổi ảnh
    mainImg.style.opacity = '0.5';
    setTimeout(() => {
        // Cập nhật class CSS để đổi hình ảnh hiển thị (theo logic máy lọc nước)
        mainImg.className = `product-silhouette product-silhouette--wide ${themeName}`;
        mainImg.style.opacity = '1';
    }, 150);

    // Xóa trạng thái "đang chọn" (active) ở các ảnh cũ và gán cho ảnh vừa nhấn
    thumbs.forEach((thumb) => thumb.classList.remove('active'));
    if (thumbElement) {
        thumbElement.classList.add('active');
    }
}

/**
 * Chuyển đổi nội dung giữa các tab: Thông số / Tính năng / Mô tả
 */
function openTab(event, tabId) {
    // 1. Tìm tất cả các vùng nội dung tab và ẩn chúng đi
    const tabContents = document.getElementsByClassName("tab-content");
    for (let content of tabContents) {
        content.classList.remove("active");
    }

    // 2. Tìm tất cả các nút tab và bỏ trạng thái "đang chọn" (active)
    const tabButtons = document.getElementsByClassName("tab-btn");
    for (let btn of tabButtons) {
        btn.classList.remove("active");
    }

    // 3. Hiển thị vùng nội dung của tab vừa nhấn và làm nổi bật nút đó
    document.getElementById(tabId).classList.add("active");
    event.currentTarget.classList.add("active");
}

// Khởi tạo mặc định (nếu cần)
document.addEventListener('DOMContentLoaded', () => {
    console.log("Giao diện đã sẵn sàng!");
});
