/**
 * QUẢN LÝ MODAL (Cửa sổ bật lên)
 * Thêm/Xóa class 'show' để điều khiển hiển thị bằng CSS (Opacity/Visibility)
 */
function openModal(id) { document.getElementById(id).classList.add('show'); }
function closeModal(id) { document.getElementById(id).classList.remove('show'); }

/**
 * Hiển thị tên file đã chọn khi người dùng upload ảnh trong Admin Inline
 * Giúp người dùng biết chắc chắn file nào đã được chọn trước khi bấm Lưu.
 */
function updateFileName(input, displayId) {
    const display = document.getElementById(displayId);
    if (input.files.length > 0) {
        display.textContent = 'Đã chọn: ' + input.files[0].name;
        display.style.color = 'var(--brand)'; // Đổi màu xanh Dahuka để nhấn mạnh
    }
}

/**
 * KHỞI TẠO CAROUSEL (Trình trình chiếu sản phẩm) TỰ ĐỘNG
 * @param {string} carouselId - ID của khung chứa sản phẩm
 * @param {string} dotsId - ID của khung chứa các nút tròn chuyển trang
 */
function initCarousel(carouselId, dotsId) {
    const carousel = document.getElementById(carouselId);
    const dotsContainer = document.getElementById(dotsId);
    if (!carousel || !dotsContainer) return;

    const items = carousel.querySelectorAll('.showcase-item');
    if (items.length === 0) return;

    // Cấu hình: Giả định hiển thị 4 sản phẩm trên mỗi "trang" màn hình (Desktop)
    const itemsPerPage = 4;
    const pageCount = Math.ceil(items.length / itemsPerPage);

    // Xóa dots cũ (nếu có) và sinh dots mới dựa trên số lượng trang thực tế
    dotsContainer.innerHTML = '';
    if (pageCount <= 1) {
        dotsContainer.style.display = 'none'; // Không cần phân trang nếu chỉ có 1 trang
        return;
    }

    for (let i = 0; i < pageCount; i++) {
        const dot = document.createElement('div');
        dot.className = 'dot' + (i === 0 ? ' active' : '');
        dot.addEventListener('click', () => {
            goToPage(i);
            resetAutoSlide(); // Reset lại thời gian tự chạy khi người dùng chủ động click
        });
        dotsContainer.appendChild(dot);
    }

    let currentIndex = 0;
    let autoSlideInterval;

    /** Chuyển đến trang chỉ định */
    function goToPage(index) {
        currentIndex = index;
        const scrollAmount = carousel.offsetWidth * index;
        // Sử dụng scrollTo với behavior 'smooth' để tạo hiệu ứng trượt mượt mà
        carousel.scrollTo({
            left: scrollAmount,
            behavior: 'smooth'
        });
        
        // Cập nhật trạng thái Active cho các nút tròn (dots)
        const dots = dotsContainer.querySelectorAll('.dot');
        dots.forEach((d, idx) => d.classList.toggle('active', idx === index));
    }

    /** Bắt đầu chu kỳ tự động chuyển trang sau mỗi 5 giây */
    function startAutoSlide() {
        autoSlideInterval = setInterval(() => {
            currentIndex = (currentIndex + 1) % pageCount;
            goToPage(currentIndex);
        }, 5000);
    }

    /** Xóa interval cũ và tạo mới để tránh xung đột thời gian */
    function resetAutoSlide() {
        clearInterval(autoSlideInterval);
        startAutoSlide();
    }

    // Kích hoạt tự động trượt ngay khi khởi tạo
    startAutoSlide();
}

// Chạy khởi tạo Carousel khi toàn bộ nội dung HTML đã sẵn sàng
document.addEventListener('DOMContentLoaded', () => {
    initCarousel('productCarousel', 'productDots');
});
