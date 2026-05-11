// --- LOGIC AJAX LỌC & SẮP XẾP SẢN PHẨM (TRANG CATALOG) ---

/** Ẩn/Hiện menu sắp xếp sản phẩm */
function toggleSort() {
    const sortOptions = document.getElementById('sortOptions');
    if (sortOptions) sortOptions.classList.toggle('show');
}

/** Cập nhật giá trị sắp xếp và kích hoạt bộ lọc mới */
function updateSort(val, label) {
    const sortInput = document.getElementById('sortInput');
    const sortLabel = document.getElementById('sortLabel');
    const sortOptions = document.getElementById('sortOptions');
    
    if (sortInput) sortInput.value = val;
    if (sortLabel) sortLabel.innerText = 'Sắp xếp: ' + label;
    if (sortOptions) sortOptions.classList.remove('show');
    
    // Kích hoạt áp dụng bộ lọc ngay lập tức
    applyFilters();
}

/** 
 * THU THẬP TẤT CẢ CÁC TIÊU CHÍ LỌC (Filter Criteria) 
 * Chuyển đổi Form thành chuỗi truy vấn (Query String) và gửi đi.
 */
function applyFilters() {
    const form = document.getElementById('filterForm');
    if (!form) return;
    
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    
    // Gọi hàm load dữ liệu bằng AJAX
    loadData(params.toString());
    
    // Cập nhật thanh địa chỉ trình duyệt (URL) mà không làm tải lại trang
    // Giúp người dùng có thể copy link đã lọc để gửi cho người khác
    const newUrl = window.location.pathname + '?' + params.toString();
    window.history.pushState({path: newUrl}, '', newUrl);
}

/** Xử lý chuyển trang (Pagination) thông qua AJAX */
function loadPage(page) {
    const form = document.getElementById('filterForm');
    if (!form) return;
    
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    params.set('page', page); // Ghi đè tham số 'page'
    
    loadData(params.toString());
    
    // Cập nhật URL
    const newUrl = window.location.pathname + '?' + params.toString();
    window.history.pushState({path: newUrl}, '', newUrl);
    
    // Tự động cuộn mượt lên đầu danh sách sản phẩm sau khi chuyển trang
    const container = document.getElementById('productListContainer');
    if (container) container.scrollIntoView({ behavior: 'smooth' });
}

/**
 * HÀM CỐT LÕI: Gửi yêu cầu AJAX lên Server để lấy HTML danh sách sản phẩm
 * @param {string} queryString - Chuỗi tham số lọc (VD: category=1&min_price=100)
 */
function loadData(queryString) {
    const overlay = document.getElementById('loadingOverlay');
    const wrapper = document.getElementById('productListWrapper');
    
    // Hiển thị hiệu ứng Loading để người dùng biết hệ thống đang xử lý
    if (overlay) overlay.classList.add('active');
    
    const baseUrl = window.location.pathname;
    
    /**
     * SỬ DỤNG FETCH API ĐỂ LẤY DỮ LIỆU BẤT ĐỒNG BỘ
     * Header 'X-Requested-With' giúp Django nhận biết đây là yêu cầu AJAX
     * để chỉ trả về file 'product_list_partial.html' thay vì toàn bộ trang.
     */
    fetch(`${baseUrl}?${queryString}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text()) // Nhận kết quả trả về dưới dạng chuỗi HTML
    .then(html => {
        // Thay thế nội dung cũ bằng nội dung mới nhận được từ Server
        if (wrapper) wrapper.innerHTML = html;
        if (overlay) overlay.classList.remove('active');
        
        // QUAN TRỌNG: Phải gán lại sự kiện click cho các nút phân trang mới vừa được render
        attachPaginationListeners();
    })
    .catch(error => {
        console.error('Lỗi khi tải danh sách sản phẩm:', error);
        if (overlay) overlay.classList.remove('active');
    });
}

/** Gán sự kiện click cho các liên kết phân trang */
function attachPaginationListeners() {
    const links = document.querySelectorAll('.pagination-link');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault(); // Ngăn chặn trình duyệt nhảy trang mặc định
            const page = this.getAttribute('data-page');
            if (page) {
                loadPage(page);
            }
        });
    });
}

// KHỞI TẠO KHI TẢI TRANG
document.addEventListener('DOMContentLoaded', function() {
    // 1. Gán sự kiện phân trang lần đầu
    attachPaginationListeners();
    
    // 2. Xử lý đóng Dropdown sắp xếp khi người dùng click ra ngoài vùng menu
    window.onclick = function(event) {
        if (!event.target.closest('.catalog-sort')) {
            const dropdowns = document.getElementsByClassName("catalog-sort-menu");
            for (let i = 0; i < dropdowns.length; i++) {
                const openDropdown = dropdowns[i];
                if (openDropdown.classList.contains('show')) {
                    openDropdown.classList.remove('show');
                }
            }
        }
    };
});
