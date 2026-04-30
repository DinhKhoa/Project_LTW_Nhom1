document.addEventListener('DOMContentLoaded', function() {
    // Expandable logic
    document.querySelectorAll('.dm-row').forEach(function(row) {
        row.addEventListener('click', function() {
            var dmId = this.getAttribute('data-dm-id');
            var detailRow = document.getElementById('detail-' + dmId);

            if (detailRow.style.display === 'none' || detailRow.style.display === '') {
                // Toggle display
                detailRow.style.display = 'table-row';
                this.classList.add('expanded');

                // Fetch products
                var tbody = detailRow.querySelector('.product-tbody');

                console.log('Fetching products for category:', dmId);
                fetch('/categories/products/' + dmId + '/')
                    .then(response => {
                        if (!response.ok) throw new Error('Network response was not ok');
                        return response.json();
                    })
                    .then(data => {
                        tbody.innerHTML = '';
                        if (!data.products || data.products.length === 0) {
                            tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4">Chưa có sản phẩm nào trong danh mục này.</td></tr>';
                            return;
                        }

                        data.products.forEach(p => {
                            const statusType = p.stock_status || 'day_du'; 
                            const statusText = p.stock_status_display || 'Đầy đủ';
                            const badgeClass = 'badge-' + statusType.replace('_', '');
                            const rowClass = (statusType === 'het_hang') ? 'row-hethang' : (statusType === 'thap' ? 'row-thap' : 'row-daydu');
                            
                            const toggleClass = p.is_active ? 'active-toggle' : '';
                            const toggleText = p.is_active ? 'Hiển thị' : 'Ẩn';
                            
                            const formattedPrice = (p.price || 0).toLocaleString('vi-VN');
                            
                            let stockDisplay = p.stock;
                            if (parseInt(p.stock) >= 999) stockDisplay = '∞';

                            const tr = document.createElement('tr');
                            tr.className = rowClass;
                            tr.style.cursor = 'pointer';
                            tr.onclick = (e) => {
                                if (!e.target.closest('.switch-wrapper')) {
                                    window.location.href = `/products/${p.id}/`;
                                }
                            };
                            
                            tr.innerHTML = `
                                <td class="text-center">${p.sku || ''}</td>
                                <td class="p-name">${p.name || ''}</td>
                                <td class="p-price text-center" style="color: #1a6b3c; font-weight: 700;">${formattedPrice} đ</td>
                                <td class="p-stock text-center">${stockDisplay}</td>
                                <td class="text-center">
                                    <div class="stock-badge ${badgeClass}" style="margin: 0 auto;">
                                        <span class="dot"></span> ${statusText}
                                    </div>
                                </td>
                                <td class="text-center">
                                    <div class="switch-wrapper ${toggleClass}" 
                                         onclick="toggleVisibility(event, ${p.id}, this)" style="margin: 0 auto;">
                                        <div class="toggle-slider"></div>
                                        <span class="toggle-label">${toggleText}</span>
                                    </div>
                                </td>
                            `;
                            tbody.appendChild(tr);
                        });
                    })
                    .catch(error => {
                        console.error('Fetch error:', error);
                        tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-danger">Lỗi khi tải dữ liệu sản phẩm.</td></tr>';
                    });
            } else {
                detailRow.style.display = 'none';
                this.classList.remove('expanded');
            }
        });
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
        } else {
            alert('Lỗi: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Có lỗi xảy ra khi cập nhật trạng thái.');
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

/* ===== Category Modal Logic ===== */
window.openCategoryModal = function(mode, id, ma, ten) {
    var modal = document.getElementById('categoryModal');
    var form = document.getElementById('categoryForm');
    var title = document.getElementById('modalTitle');
    var tenInput = document.getElementById('category_name');
    var submitBtn = document.getElementById('submitBtn');

    if (mode === 'edit') {
        title.textContent = 'CHỈNH SỬA DANH MỤC';
        form.action = '/categories/edit/' + id + '/';
        tenInput.value = ten;
        submitBtn.innerHTML = 'Cập nhật';
    } else {
        title.textContent = 'THÊM DANH MỤC MỚI';
        form.action = '/categories/add/';
        tenInput.value = '';
        submitBtn.innerHTML = 'Thêm mới';
    }

    modal.classList.add('show');
};

window.closeCategoryModal = function() {
    document.getElementById('categoryModal').classList.remove('show');
};

window.openDeleteModal = function(id, name) {
    var modal = document.getElementById('deleteModal');
    var form = document.getElementById('deleteForm');
    var nameSpan = document.getElementById('deleteTargetName');

    form.action = '/categories/delete/' + id + '/';
    nameSpan.textContent = name;
    modal.classList.add('show');
};

window.closeDeleteModal = function() {
    document.getElementById('deleteModal').classList.remove('show');
};

// Close on outside click
window.onclick = function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        closeCategoryModal();
        closeDeleteModal();
    }
};
