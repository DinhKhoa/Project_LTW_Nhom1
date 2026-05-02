// --- LOGIC AJAX LỌC & SẮP XẾP SẢN PHẨM (TRANG CATALOG) ---

function toggleSort() {
    const sortOptions = document.getElementById('sortOptions');
    if (sortOptions) sortOptions.classList.toggle('show');
}

function updateSort(val, label) {
    const sortInput = document.getElementById('sortInput');
    const sortLabel = document.getElementById('sortLabel');
    const sortOptions = document.getElementById('sortOptions');
    
    if (sortInput) sortInput.value = val;
    if (sortLabel) sortLabel.innerText = 'Sắp xếp: ' + label;
    if (sortOptions) sortOptions.classList.remove('show');
    applyFilters();
}

function applyFilters() {
    const form = document.getElementById('filterForm');
    if (!form) return;
    
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    
    loadData(params.toString());
    
    // Update URL without reloading
    const newUrl = window.location.pathname + '?' + params.toString();
    window.history.pushState({path: newUrl}, '', newUrl);
}

function loadPage(page) {
    const form = document.getElementById('filterForm');
    if (!form) return;
    
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    params.set('page', page);
    
    loadData(params.toString());
    
    // Update URL
    const newUrl = window.location.pathname + '?' + params.toString();
    window.history.pushState({path: newUrl}, '', newUrl);
    
    // Scroll to top of product list
    const container = document.getElementById('productListContainer');
    if (container) container.scrollIntoView({ behavior: 'smooth' });
}

function loadData(queryString) {
    const overlay = document.getElementById('loadingOverlay');
    const wrapper = document.getElementById('productListWrapper');
    if (overlay) overlay.classList.add('active');
    
    const baseUrl = window.location.pathname;
    
    fetch(`${baseUrl}?${queryString}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        if (wrapper) wrapper.innerHTML = html;
        if (overlay) overlay.classList.remove('active');
        
        // Re-attach pagination listeners after AJAX update
        attachPaginationListeners();
    })
    .catch(error => {
        console.error('Error fetching products:', error);
        if (overlay) overlay.classList.remove('active');
    });
}

function attachPaginationListeners() {
    const links = document.querySelectorAll('.pagination-link');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            if (page) {
                loadPage(page);
            }
        });
    });
}

// --- KHỞI TẠO ---
document.addEventListener('DOMContentLoaded', function() {
    // 1. Gán sự kiện phân trang
    attachPaginationListeners();
    
    // 2. Đóng dropdown khi click ngoài
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
