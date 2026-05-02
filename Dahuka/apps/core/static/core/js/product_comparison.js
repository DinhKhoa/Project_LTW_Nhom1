let currentReplaceIndex = -1;
let currentProductIds = [];

document.addEventListener('DOMContentLoaded', function() {
    const idsData = document.getElementById('current-product-ids');
    if (idsData) {
        currentProductIds = JSON.parse(idsData.textContent).map(id => id.toString());
    }

    // Close on escape
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeSelectionModal();
    });
});

function openSelectionModal(index = -1) {
    currentReplaceIndex = index;
    const modal = document.getElementById('selectionModal');
    if (modal) modal.classList.add('active');
}

function closeSelectionModal() {
    const modal = document.getElementById('selectionModal');
    if (modal) modal.classList.remove('active');
}

function selectProduct(id) {
    if (currentProductIds.includes(id)) {
        window.showToast('Sản phẩm này đã có trong danh sách so sánh!', 'warning');
        return;
    }

    let newIds = [...currentProductIds];
    if (currentReplaceIndex >= 0) {
        newIds[currentReplaceIndex] = id;
    } else {
        newIds.push(id);
    }

    updateUrlAndReload(newIds);
}

function removeItem(id) {
    const newIds = currentProductIds.filter(i => i !== id);
    updateUrlAndReload(newIds);
}

function updateUrlAndReload(ids) {
    // Đồng bộ hóa với thanh so sánh toàn cục (localStorage)
    let compareItems = JSON.parse(localStorage.getItem('compareItems') || '[]');
    // Lọc bỏ những id không còn trong danh sách mới
    compareItems = compareItems.filter(item => ids.includes(item.id.toString()));
    localStorage.setItem('compareItems', JSON.stringify(compareItems));
    
    localStorage.setItem('compareIds', JSON.stringify(ids));
    
    const params = new URLSearchParams();
    ids.forEach(id => params.append('id', id));
    window.location.href = window.location.pathname + '?' + params.toString();
}

// Export functions to window for onclick handlers in HTML
window.openSelectionModal = openSelectionModal;
window.closeSelectionModal = closeSelectionModal;
window.selectProduct = selectProduct;
window.removeItem = removeItem;
