/* ===== Xử lý click vào hàng trong bảng ===== */
window.handleRowClick = function(event, url) {
    // Nếu người dùng nhấn trúng nút "Ẩn/Hiện" thì không chuyển trang
    if (!event.target.closest('.switch-wrapper')) {
        window.location.href = url;
    }
};

/* ===== Logic của các bộ lọc (Filter) ===== */
window.toggleFilterDropdown = function(id) {
    var wrapper = document.getElementById(id);
    var btn = wrapper.querySelector('.filter-dropdown-btn');
    var menu = wrapper.querySelector('.filter-dropdown-menu');

    // Đóng tất cả các menu lọc khác trước khi mở menu hiện tại
    document.querySelectorAll('.filter-dropdown-wrapper').forEach(function (w) {
        if (w.id !== id) {
            w.querySelector('.filter-dropdown-btn').classList.remove('open');
            w.querySelector('.filter-dropdown-menu').classList.remove('show');
        }
    });

    btn.classList.toggle('open');
    menu.classList.toggle('show');
};

// Chọn một giá trị trong menu lọc (ví dụ: lọc theo Máy lọc nước)
window.selectFilterItem = function(item, wrapperId) {
    var wrapper = document.getElementById(wrapperId);
    wrapper.querySelectorAll('.filter-item').forEach(el => el.classList.remove('selected'));
    item.classList.add('selected');
    applyFilters(); // Sau khi chọn xong thì áp dụng lọc ngay
};

// Tổng hợp tất cả giá trị lọc và gửi yêu cầu tải lại trang
window.applyFilters = function() {
    const query = document.getElementById('searchInput').value.trim(); // Lấy từ khóa tìm kiếm
    const category = document.getElementById('categoryFilter').querySelector('.filter-item.selected').getAttribute('data-value');
    const inventory = document.getElementById('inventoryFilter').querySelector('.filter-item.selected').getAttribute('data-value');

    // Xây dựng URL mới với các tham số ?q=...&category=...
    let url = new URL(window.location.origin + window.location.pathname);
    if (query) url.searchParams.set('q', query);
    if (category !== 'all') url.searchParams.set('category', category);
    if (inventory !== 'default') url.searchParams.set('inventory', inventory);
    
    // Chuyển hướng trình duyệt đến URL mới đã lọc
    window.location.href = url.toString();
};

window.removeFilter = function(type) {
    let url = new URL(window.location.href);
    if (type === 'category') url.searchParams.delete('category');
    if (type === 'inventory') url.searchParams.delete('inventory');
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
};

/* ===== Setup Event Listeners ===== */
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });

        // Initialize search input from URL
        const params = new URLSearchParams(window.location.search);
        if (params.has('q')) {
            searchInput.value = params.get('q');
        }
    }

    // Close on outside click
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.filter-dropdown-wrapper')) {
            document.querySelectorAll('.filter-dropdown-wrapper').forEach(function(w) {
                w.querySelector('.filter-dropdown-btn').classList.remove('open');
                w.querySelector('.filter-dropdown-menu').classList.remove('show');
            });
        }
    });
});

/* ===== Thay đổi trạng thái Ẩn/Hiện bằng AJAX (Không tải lại trang) ===== */
window.toggleVisibility = function(event, productId, element) {
    event.stopPropagation(); // Ngăn việc nhấn nút làm kích hoạt luôn sự kiện nhấn vào hàng bảng
    const isVisible = !element.classList.contains('active-toggle');
    const label = element.querySelector('.toggle-label');

    // Dùng hàm fetch() để gửi yêu cầu POST bí mật tới Backend (Django)
    fetch(`/products/toggle-visibility/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Gửi token bảo mật để Django không từ chối
        },
        body: JSON.stringify({ is_visible: isVisible }) // Đóng gói dữ liệu trạng thái mới
    })
    .then(response => response.json())
    .then(data => {
        // Nếu Server báo thành công, tiến hành đổi màu nút bấm trên màn hình
        if (data.status === 'success') {
            if (data.is_active) {
                element.classList.add('active-toggle');
                label.textContent = 'Hiển thị';
            } else {
                element.classList.remove('active-toggle');
                label.textContent = 'Ẩn';
            }
        }
    });
};

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
