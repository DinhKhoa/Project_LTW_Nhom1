// Logic so sánh sản phẩm toàn cục cho Dahuka
const MAX_COMPARE = 3;

function syncGlobalCompare() {
    const items = JSON.parse(localStorage.getItem('compareItems') || '[]');
    const bar = document.getElementById('compareBar');
    const list = document.getElementById('compareItemsList');
    const countLabel = document.getElementById('compareCountLabel');
    const btnGo = document.getElementById('btnCompareGo');
    const form = document.getElementById('compareForm');

    if (!bar) return;

    if (items.length > 0) {
        bar.classList.add('active');
    } else {
        bar.classList.remove('active');
    }

    if (countLabel) countLabel.textContent = `Đã chọn ${items.length} sản phẩm`;

    if (btnGo) {
        if (items.length >= 2) {
            btnGo.style.opacity = '1';
            btnGo.style.pointerEvents = 'auto';
        } else {
            btnGo.style.opacity = '0.5';
            btnGo.style.pointerEvents = 'none';
        }
    }

    if (form) {
        const container = document.getElementById('hiddenIdInputs') || form;
        container.querySelectorAll('input[name="id"]').forEach(el => el.remove());
        items.forEach(item => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'id';
            input.value = item.id;
            container.appendChild(input);
        });
    }

    if (list) {
        list.innerHTML = '';
        items.forEach(item => {
            const el = document.createElement('div');
            el.className = 'compare-item-card';
            el.innerHTML = `
                <img src="${item.img}" alt="product" style="width:100%; height:100%; object-fit:cover; border-radius:8px;">
                <div class="remove-item" data-id="${item.id}"><i class="fa fa-times"></i></div>
            `;
            list.appendChild(el);
        });
        
        for (let i = items.length; i < MAX_COMPARE; i++) {
            const empty = document.createElement('div');
            empty.className = 'compare-item-card empty-slot';
            list.appendChild(empty);
        }
    }
}

// Lắng nghe sự kiện click toàn cục
document.addEventListener('click', function(e) {
    // 1. Nút thêm vào so sánh
    const addBtn = e.target.closest('.compare-btn');
    if (addBtn) {
        const card = addBtn.closest('[data-id]');
        if (!card) return;
        
        const pid = card.getAttribute('data-id');
        const pimg = card.getAttribute('data-img') || '/static/img/no-image.png';
        if (!pid) return;

        let items = JSON.parse(localStorage.getItem('compareItems') || '[]');
        
        // Kiểm tra trùng (dùng String để so sánh chuẩn xác)
        if (items.find(i => String(i.id) === String(pid))) {
            window.showToast('Sản phẩm này đã có trong danh sách so sánh!', 'warning');
            return;
        }

        if (items.length >= MAX_COMPARE) {
            window.showToast(`Bạn chỉ có thể so sánh tối đa ${MAX_COMPARE} sản phẩm!`, 'error');
            return;
        }

        items.push({ id: String(pid), img: pimg });
        localStorage.setItem('compareItems', JSON.stringify(items));
        syncGlobalCompare();
        
        window.showToast('Đã thêm sản phẩm vào danh sách so sánh', 'success');
    }

    // 2. Nút xóa từng sản phẩm trên thanh so sánh
    const removeBtn = e.target.closest('.remove-item');
    if (removeBtn) {
        const pid = removeBtn.getAttribute('data-id');
        let items = JSON.parse(localStorage.getItem('compareItems') || '[]');
        items = items.filter(i => String(i.id) !== String(pid));
        localStorage.setItem('compareItems', JSON.stringify(items));
        syncGlobalCompare();
    }

    // 3. Nút xóa tất cả
    if (e.target.id === 'btnClearAll') {
        localStorage.removeItem('compareItems');
        syncGlobalCompare();
        window.showToast('Đã xóa danh sách so sánh', 'success');
    }
});

// Khởi tạo khi tải trang
document.addEventListener('DOMContentLoaded', syncGlobalCompare);
