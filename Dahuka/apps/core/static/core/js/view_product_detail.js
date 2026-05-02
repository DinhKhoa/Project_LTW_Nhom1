function updateMainImage(thumbElement) {
    const img = thumbElement.querySelector('img');
    const mainImg = document.getElementById('mainImg');
    if (img && mainImg) {
        mainImg.src = img.src;
        // Update active state
        document.querySelectorAll('.thumb-box').forEach(el => el.classList.remove('active'));
        thumbElement.classList.add('active');
    }
}

function openTab(btn, tabId) {
    // Toggle Buttons - support both legacy and minimal classes
    document.querySelectorAll('.tab-btn, .tab-btn-minimal').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // Toggle Contents - support both legacy and minimal classes
    document.querySelectorAll('.tab-content, .tab-content-minimal').forEach(c => c.classList.remove('active'));
    const target = document.getElementById(tabId);
    if (target) {
        target.classList.add('active');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Initialization logic if needed
});