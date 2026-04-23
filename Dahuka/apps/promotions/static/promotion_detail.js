document.addEventListener('DOMContentLoaded', () => {
    const productGrid = document.getElementById('productGrid');
    const btnAddProduct = document.getElementById('btnAddProduct');
    const showAppConfirm = window.showAppConfirm;
    const showAppToast = window.showAppToast;

    /**
     * Chức năng xóa sản phẩm (Xử lý cho các phần tử có sẵn và tạo mới)
     */
    productGrid.addEventListener('click', (e) => {
        const deleteButton = e.target.closest('.btn-delete');
        if (deleteButton) {
            const card = e.target.closest('.product-card');
            const item = deleteButton.closest('.promo-product-item');
            showAppConfirm({
                title: 'Xác nhận xóa sản phẩm',
                message: 'Nếu chọn Xác nhận, sản phẩm sẽ bị xóa khỏi giao diện.',
                onConfirm: () => {
                    const target = card || item;
                    if (target) {
                        target.style.opacity = '0';
                        setTimeout(() => {
                            target.remove();
                            showAppToast('Xóa thành công');
                        }, 250);
                    }
                }
            });
        }
    });

    /**
     * Chức năng thêm sản phẩm mẫu để test Grid 3 cột
     */
    btnAddProduct.addEventListener('click', () => {
        const newProduct = document.createElement('div');
        newProduct.className = 'promo-product-item';
        newProduct.innerHTML = `
            <span>Máy lọc nước Hydrogen Alkaline Mutosi mới</span>
            <button class="btn-delete" type="button">✕</button>
        `;
        productGrid.appendChild(newProduct);
    });

    /**
     * Hiệu ứng khi hover vào các nút chính (Lưu, Quay lại)
     * Đã được xử lý chủ yếu qua CSS, JS có thể dùng để log hoặc xử lý logic lưu trữ.
     */
    const saveBtn = document.querySelector('.btn-save');
    saveBtn.addEventListener('click', () => {
        showAppToast('Lưu thành công');
    });

    const backBtn = document.querySelector('.btn-back');
    if (backBtn) {
        backBtn.addEventListener('click', () => window.history.back());
    }

    const discountType = document.getElementById('discountType');
    if (discountType) {
        discountType.addEventListener('change', updateUnit);
        // Initial run
        updateUnit();
    }
});

function updateUnit() {
    const type = document.getElementById('discountType').value;
    const unit = document.getElementById('discountUnit');
    const discountValue = document.getElementById('discountValue');
    
    if (type === 'percent') {
        if (unit) unit.textContent = '%';
        if (discountValue) discountValue.removeEventListener("input", formatCurrencyHandler);
    } else {
        if (unit) unit.textContent = 'VND';
        if (discountValue) discountValue.addEventListener("input", formatCurrencyHandler);
    }
}

function formatCurrency(input) {
    let value = input.value.replace(/\D/g, "");
    if (value) {
        input.value = new Intl.NumberFormat('vi-VN').format(value);
    }
}

function formatCurrencyHandler(e) {
    formatCurrency(e.target);
}

