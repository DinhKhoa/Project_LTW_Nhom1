function updateMainImage(thumbElement) {
    const img = thumbElement.querySelector('img');
    const mainImg = document.getElementById('mainImg');
    if (img && mainImg) {
        mainImg.src = img.src;
        // Update active state
        document.querySelectorAll('.thumb-item').forEach(el => el.classList.remove('active'));
        thumbElement.classList.add('active');
    }
}

function openTab(btn, tabId) {
    // Toggle Buttons
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // Toggle Contents
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    const target = document.getElementById(tabId);
    if (target) {
        target.classList.add('active');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Any initialization logic for detail page
});
