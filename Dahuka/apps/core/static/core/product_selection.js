let selectedCount = 0;

window.toggleItem = function(el) {
    if (el.classList.contains('selected')) {
        el.classList.remove('selected');
        selectedCount--;
    } else {
        if (selectedCount < 3) {
            el.classList.add('selected');
            selectedCount++;
        } else {
            if (typeof showToast === 'function') {
                showToast('Chỉ được chọn tối đa 3 sản phẩm để so sánh!', 'warning');
            } else {
                alert('Chỉ được chọn tối đa 3 sản phẩm để so sánh!');
            }
        }
    }
    const countEl = document.getElementById('selection-count');
    if (countEl) {
        countEl.innerText = `Đã chọn: ${selectedCount}/3`;
    }
};

window.goToCompare = function() {
    const selectedItems = document.querySelectorAll('.frame-item.selected');
    if (selectedItems.length < 2) {
        if (typeof showToast === 'function') {
            showToast('Vui lòng chọn ít nhất 2 sản phẩm để so sánh!', 'warning');
        } else {
            alert('Vui lòng chọn ít nhất 2 sản phẩm để so sánh!');
        }
        return;
    }
    
    const params = new URLSearchParams();
    selectedItems.forEach(item => {
        params.append('id', item.dataset.id);
    });
    
    window.location.href = "/comparison/?" + params.toString();
};
