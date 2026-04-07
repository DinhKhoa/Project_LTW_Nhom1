/**
 * Yêu cầu 1: Thay đổi ảnh chính khi di chuột qua ảnh nhỏ
 */
function changeImage(themeName, thumbElement) {
    const mainImg = document.getElementById('main-product-img');
    const thumbs = document.querySelectorAll('.thumb');
    mainImg.style.opacity = '0.5';
    setTimeout(() => {
        mainImg.className = `product-silhouette product-silhouette--wide ${themeName}`;
        mainImg.style.opacity = '1';
    }, 150);

    thumbs.forEach((thumb) => thumb.classList.remove('active'));
    if (thumbElement) {
        thumbElement.classList.add('active');
    }
}

/**
 * Yêu cầu 3: Bấm vào Thông số/ Tính năng/ Mô tả để hiện nội dung tương ứng
 */
function openTab(event, tabId) {
    // 1. Lấy tất cả các phần tử nội dung tab và ẩn chúng đi
    const tabContents = document.getElementsByClassName("tab-content");
    for (let content of tabContents) {
        content.classList.remove("active");
    }

    // 2. Lấy tất cả các nút tab và bỏ class 'active'
    const tabButtons = document.getElementsByClassName("tab-btn");
    for (let btn of tabButtons) {
        btn.classList.remove("active");
    }

    // 3. Hiển thị nội dung tab hiện tại và đánh dấu nút đang được chọn
    document.getElementById(tabId).classList.add("active");
    event.currentTarget.classList.add("active");
}

// Khởi tạo mặc định (nếu cần)
document.addEventListener('DOMContentLoaded', () => {
    console.log("Giao diện đã sẵn sàng!");
});
