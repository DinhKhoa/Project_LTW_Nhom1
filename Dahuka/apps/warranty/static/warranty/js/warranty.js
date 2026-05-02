document.addEventListener('DOMContentLoaded', function() {
    console.log('Dahuka Support Page Loaded');

    const editModal = document.getElementById('editWarrantySettingsModal');
    const openBtn = document.querySelector('.admin-edit-btn');
    const closeBtns = document.querySelectorAll('.warranty-modal-close, .btn-dahuka-outline');

    if (openBtn && editModal) {
        openBtn.addEventListener('click', function() {
            editModal.style.display = 'flex';
        });
    }

    if (closeBtns && editModal) {
        closeBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                editModal.style.display = 'none';
            });
        });
    }

    // Close modal when clicking outside the box
    window.addEventListener('click', function(event) {
        if (event.target === editModal) {
            editModal.style.display = 'none';
        }
    });
});
