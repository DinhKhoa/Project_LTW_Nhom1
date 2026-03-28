/**
 * Dahuka Support Page - Interactivity
 * Focus: Smooth animations and map pin effects
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dahuka Support Page Loaded');

    // Add subtle hover effect for map popup reveal
    const mapFrame = document.querySelector('.map-frame');
    const mapPopup = document.querySelector('.map-popup');
    const mapPin = document.querySelector('.map-pin');

    if (mapFrame && mapPopup && mapPin) {
        mapFrame.addEventListener('mouseenter', () => {
            mapPopup.style.opacity = '1';
            mapPopup.style.transform = 'translateY(0)';
        });

        mapPin.addEventListener('mouseenter', () => {
            mapPin.style.transform = 'translate(-50%, -50%) scale(1.3)';
            mapPopup.style.boxShadow = '0 20px 40px rgba(11, 110, 79, 0.2)';
        });

        mapPin.addEventListener('mouseleave', () => {
            mapPin.style.transform = 'translate(-50%, -50%) scale(1)';
            mapPopup.style.boxShadow = '0 15px 35px rgba(0,0,0,0.08)';
        });
    }

    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll('.gallery-card, .support-map-card, .support-info-card');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.8s cubic-bezier(0.16, 1, 0.3, 1)';
        observer.observe(el);
    });

    // Custom CSS for Intersection Observer
    const style = document.createElement('style');
    style.innerHTML = `
        .is-visible {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(style);
});
