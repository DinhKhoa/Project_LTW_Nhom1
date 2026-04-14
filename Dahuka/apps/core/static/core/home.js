function openModal(id) { document.getElementById(id).classList.add('show'); }
function closeModal(id) { document.getElementById(id).classList.remove('show'); }

function updateFileName(input, displayId) {
    const display = document.getElementById(displayId);
    if (input.files.length > 0) {
        display.textContent = 'Đã chọn: ' + input.files[0].name;
        display.style.color = 'var(--brand)';
    }
}

// Auto-carousel logic
function initCarousel(dotsId) {
    const dots = document.querySelectorAll(`#${dotsId} .dot`);
    let currentIndex = 0;
    function setActive(index) {
        dots.forEach(d => d.classList.remove('active'));
        if(dots[index]) dots[index].classList.add('active');
    }
    dots.forEach((dot, idx) => {
        dot.addEventListener('click', () => { currentIndex = idx; setActive(currentIndex); });
    });
    setInterval(() => {
        if(dots.length > 0) {
            currentIndex = (currentIndex + 1) % dots.length;
            setActive(currentIndex);
        }
    }, 5000);
}

document.addEventListener('DOMContentLoaded', () => {
    initCarousel('productDots');
});
