const compareItems = [];
const maxItems = 3;
const compareBar = document.getElementById('compareBar');
const compareItemsList = document.getElementById('compareItemsList');
const compareCountLabel = document.getElementById('compareCountLabel');
const btnCompareGo = document.getElementById('btnCompareGo');
const btnClearAll = document.getElementById('btnClearAll');

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.compare-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const card = e.target.closest('.catalog-card');
            const product = {
                id: card.dataset.id,
                name: card.dataset.name,
                img: card.dataset.img,
                price: card.dataset.price
            };

            if (compareItems.find(item => item.id === product.id)) {
                return; // Already added
            }

            if (compareItems.length >= maxItems) {
                alert(`Bạn chỉ có thể chọn tối đa ${maxItems} sản phẩm để so sánh.`);
                return;
            }

            compareItems.push(product);
            updateCompareBar();
        });
    });

    if (btnClearAll) {
        btnClearAll.addEventListener('click', () => {
            compareItems.length = 0;
            updateCompareBar();
        });
    }
});

function updateCompareBar() {
    if (!compareBar) return;

    if (compareItems.length > 0) {
        compareBar.classList.add('active');
    } else {
        compareBar.classList.remove('active');
    }

    compareItemsList.innerHTML = '';
    compareItems.forEach(item => {
        const el = document.createElement('div');
        el.className = 'compare-item-card';
        el.innerHTML = `
            <img src="${item.img}" alt="${item.name}">
            <div class="remove-btn" onclick="removeItem('${item.id}')"><i class="fa fa-times"></i></div>
        `;
        compareItemsList.appendChild(el);
    });

    // Fill empty slots
    for (let i = compareItems.length; i < maxItems; i++) {
        const el = document.createElement('div');
        el.className = 'compare-item-card';
        el.style.background = 'rgba(0,0,0,0.03)';
        el.style.borderStyle = 'dashed';
        compareItemsList.appendChild(el);
    }

    compareCountLabel.textContent = `Đã chọn ${compareItems.length} sản phẩm`;
    
    if (compareItems.length >= 2) {
        btnCompareGo.style.opacity = '1';
        btnCompareGo.style.pointerEvents = 'auto';
    } else {
        btnCompareGo.style.opacity = '0.5';
        btnCompareGo.style.pointerEvents = 'none';
    }
}

window.removeItem = (id) => {
    const index = compareItems.findIndex(item => item.id === id);
    if (index > -1) {
        compareItems.splice(index, 1);
        updateCompareBar();
    }
};
