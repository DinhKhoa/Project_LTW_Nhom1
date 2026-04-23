let selectedCount = 1;

window.toggleItem = function(el) {
    if (el.classList.contains('selected')) {
        el.classList.remove('selected');
        selectedCount--;
    } else {
        if (selectedCount < 3) {
            el.classList.add('selected');
            selectedCount++;
        } else {
            alert('Chỉ được chọn tối đa 3 sản phẩm để so sánh!');
        }
    }
    const countEl = document.getElementById('selection-count');
    if (countEl) {
        countEl.innerText = `Đã chọn: ${selectedCount}/3`;
    }
};

window.goToCompare = function() {
    if (selectedCount < 2) {
        alert('Vui lòng chọn ít nhất 2 sản phẩm để so sánh!');
        return;
    }
    window.location.href = "/comparison/";
};
