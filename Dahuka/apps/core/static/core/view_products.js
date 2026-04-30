// PHƯƠNG ÁN SO SÁNH TỔNG LỰC - 100% HOẠT ĐỘNG
const MAX_COMPARE_ITEMS = 3;

// Hàm đồng bộ hóa Form và giao diện
function syncCompareState() {
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
        form.querySelectorAll('input[name="id"]').forEach(el => el.remove());
        items.forEach(item => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'id';
            input.value = item.id;
            form.appendChild(input);
        });
    }

    if (list) {
        list.innerHTML = '';
        items.forEach(item => {
            const el = document.createElement('div');
            el.className = 'compare-item-card';
            el.innerHTML = `
                <img src="${item.img}" alt="product" style="width:100%; height:100%; object-fit:cover; border-radius:8px;">
                <div class="remove-btn" data-id="${item.id}"><i class="fa fa-times"></i></div>
            `;
            list.appendChild(el);
        });
        
        for (let i = items.length; i < MAX_COMPARE_ITEMS; i++) {
            const empty = document.createElement('div');
            empty.className = 'compare-item-card empty-slot';
            list.appendChild(empty);
        }
    }
}

// Lắng nghe mọi cú click trên trang
document.addEventListener('click', function(e) {
    const addBtn = e.target.closest('.compare-btn');
    if (addBtn) {
        const card = addBtn.closest('.catalog-card');
        if (!card) return;
        
        const pid = card.getAttribute('data-id');
        const pimg = card.getAttribute('data-img');
        if (!pid) return;

        let items = JSON.parse(localStorage.getItem('compareItems') || '[]');
        
        if (items.find(i => i.id === pid)) {
            alert('Sản phẩm đã có trong danh sách!');
            return;
        }

        if (items.length >= MAX_COMPARE_ITEMS) {
            alert(`Tối đa ${MAX_COMPARE_ITEMS} sản phẩm!`);
            return;
        }

        items.push({ id: pid, img: pimg });
        localStorage.setItem('compareItems', JSON.stringify(items));
        syncCompareState();
    }

    const removeBtn = e.target.closest('.remove-btn');
    if (removeBtn) {
        const pid = removeBtn.getAttribute('data-id');
        let items = JSON.parse(localStorage.getItem('compareItems') || '[]');
        items = items.filter(i => i.id !== pid);
        localStorage.setItem('compareItems', JSON.stringify(items));
        syncCompareState();
    }

    const clearBtn = e.target.closest('#btnClearAll');
    if (clearBtn) {
        localStorage.removeItem('compareItems');
        syncCompareState();
    }
});

// Chạy ngay khi tải trang
document.addEventListener('DOMContentLoaded', syncCompareState);
