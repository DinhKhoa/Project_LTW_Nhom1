function openModal(id) { document.getElementById(id).classList.add('show'); }
function closeModal(id) { document.getElementById(id).classList.remove('show'); }

function updateFileName(input, displayId) {
    const display = document.getElementById(displayId);
    if (input.files.length > 0) {
        display.textContent = 'Đã chọn: ' + input.files[0].name;
        display.style.color = 'var(--brand)';
    }
}

// Auto-carousel logic nâng cao cho Dahuka
function initCarousel(carouselId, dotsId) {
    const carousel = document.getElementById(carouselId);
    const dotsContainer = document.getElementById(dotsId);
    if (!carousel || !dotsContainer) return;

    const items = carousel.querySelectorAll('.showcase-item');
    if (items.length === 0) return;

    // Giả định 4 sản phẩm/trang trên desktop
    const itemsPerPage = 4;
    const pageCount = Math.ceil(items.length / itemsPerPage);

    // Xóa dots cũ (nếu có) và sinh dots mới
    dotsContainer.innerHTML = '';
    if (pageCount <= 1) {
        dotsContainer.style.display = 'none';
        return;
    }

    for (let i = 0; i < pageCount; i++) {
        const dot = document.createElement('div');
        dot.className = 'dot' + (i === 0 ? ' active' : '');
        dot.addEventListener('click', () => {
            goToPage(i);
            resetAutoSlide();
        });
        dotsContainer.appendChild(dot);
    }

    let currentIndex = 0;
    let autoSlideInterval;

    function goToPage(index) {
        currentIndex = index;
        const scrollAmount = carousel.offsetWidth * index;
        carousel.scrollTo({
            left: scrollAmount,
            behavior: 'smooth'
        });
        
        // Cập nhật trạng thái dot
        const dots = dotsContainer.querySelectorAll('.dot');
        dots.forEach((d, idx) => d.classList.toggle('active', idx === index));
    }

    function startAutoSlide() {
        autoSlideInterval = setInterval(() => {
            currentIndex = (currentIndex + 1) % pageCount;
            goToPage(currentIndex);
        }, 5000);
    }

    function resetAutoSlide() {
        clearInterval(autoSlideInterval);
        startAutoSlide();
    }

    startAutoSlide();
}

document.addEventListener('DOMContentLoaded', () => {
    initCarousel('productCarousel', 'productDots');
});
