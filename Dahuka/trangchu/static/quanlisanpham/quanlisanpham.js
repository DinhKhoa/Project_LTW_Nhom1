document.addEventListener('DOMContentLoaded', () => {
    const btnAddProduct = document.getElementById('btnAddProduct');
    const productGrid = document.getElementById('productGrid');
    const saveBtn = document.querySelector('.btn-save');
    const backBtn = document.querySelector('.btn-back');
    const showAppConfirm = window.showAppConfirm;
    const showAppToast = window.showAppToast;

    const demoProducts = [
        "Máy lọc nước Hydrogen Alkaline",
        "Máy lọc nước nóng lạnh 3 chế độ",
        "Máy lọc nước để gầm cao cấp",
        "Lõi lọc Cation",
        "Lõi lọc Nano Silver",
        "Lõi khoáng đá Maifan",
        "Màng RO Mutosi",
        "Bơm tăng áp 24V",
        "Van áp thấp",
        "Bình áp 10 lít",
        "Cút nối nhanh 1/4",
        "Đèn UV diệt khuẩn"
    ];

    const trashIcon = `
        <span class="trash-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
                <path d="M9 3h6l1 2h4v2H4V5h4l1-2Z" />
                <path d="M7 9h10l-1 10a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2L7 9Z" />
                <path d="M10 11v6M14 11v6" />
            </svg>
        </span>
    `;

    let nextProductIndex = 0;

    function attachDeleteHandler(button) {
        button.addEventListener('click', function () {
            const targetItem = this.closest('.product-item');
            showAppConfirm({
                title: 'Xác nhận xóa sản phẩm',
                message: 'Nếu chọn Xác nhận, sản phẩm sẽ bị xóa khỏi giao diện.',
                onConfirm: () => {
                    if (targetItem) {
                        targetItem.remove();
                        showAppToast('Xóa thành công');
                    }
                }
            });
        });
    }

    function createProductItem(productName) {
        const productItem = document.createElement('div');
        productItem.className = 'product-item';
        productItem.innerHTML = `
            <span class="product-name">${productName}</span>
            <button class="btn-delete" type="button" aria-label="Xóa sản phẩm">${trashIcon}</button>
        `;
        attachDeleteHandler(productItem.querySelector('.btn-delete'));
        return productItem;
    }

    btnAddProduct.addEventListener('click', () => {
        const productName = demoProducts[nextProductIndex % demoProducts.length];
        nextProductIndex += 1;
        productGrid.appendChild(createProductItem(productName));
    });

    const initialDeleteBtns = document.querySelectorAll('.btn-delete');
    initialDeleteBtns.forEach(btn => {
        attachDeleteHandler(btn);
    });

    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            showAppToast('Lưu thành công');
        });
    }

    if (backBtn) {
        backBtn.addEventListener('click', () => window.history.back());
    }
});
