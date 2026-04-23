/* ===== Handle Row Click ===== */
window.handleRowClick = function(event, url) {
    if (!event.target.closest('.switch-wrapper')) {
        window.location.href = url;
    }
};

/* ===== Filter Dropdowns ===== */
window.toggleFilterDropdown = function(id) {
    var wrapper = document.getElementById(id);
    var btn = wrapper.querySelector('.filter-dropdown-btn');
    var menu = wrapper.querySelector('.filter-dropdown-menu');

    document.querySelectorAll('.filter-dropdown-wrapper').forEach(function (w) {
        if (w.id !== id) {
            w.querySelector('.filter-dropdown-btn').classList.remove('open');
            w.querySelector('.filter-dropdown-menu').classList.remove('show');
        }
    });

    btn.classList.toggle('open');
    menu.classList.toggle('show');
};

window.selectFilterItem = function(item, wrapperId) {
    var wrapper = document.getElementById(wrapperId);
    wrapper.querySelectorAll('.filter-item').forEach(el => el.classList.remove('selected'));
    item.classList.add('selected');
    applyFilters();
};

window.applyFilters = function() {
    const query = document.getElementById('searchInput').value.trim();
    const category = document.getElementById('categoryFilter').querySelector('.filter-item.selected').getAttribute('data-value');
    const inventory = document.getElementById('inventoryFilter').querySelector('.filter-item.selected').getAttribute('data-value');

    let url = new URL(window.location.origin + window.location.pathname);
    if (query) url.searchParams.set('q', query);
    if (category !== 'all') url.searchParams.set('category', category);
    if (inventory !== 'default') url.searchParams.set('inventory', inventory);
    
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

/* ===== Toggle Visibility AJAX ===== */
window.toggleVisibility = function(event, productId, element) {
    event.stopPropagation();
    const isVisible = !element.classList.contains('active-toggle');
    const label = element.querySelector('.toggle-label');

    fetch(`/products/toggle-visibility/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ is_visible: isVisible })
    })
    .then(response => response.json())
    .then(data => {
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
