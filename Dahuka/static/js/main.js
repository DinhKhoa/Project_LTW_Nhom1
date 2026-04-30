/* 
 * Dahuka Security: Prevent unauthorized inspection
 * Inspired by Facebook's Console Warning
 */

// // 1. Disable Right-Click
// document.addEventListener('contextmenu', event => {
//     event.preventDefault();
// });

// // 2. Disable Keyboard Shortcuts (F12, Ctrl+Shift+I/J/C, Ctrl+U)
// document.addEventListener('keydown', event => {
//     // F12
//     if (event.keyCode === 123) {
//         event.preventDefault();
//         return false;
//     }
//     // Ctrl+Shift+I (Inspect), Ctrl+Shift+J (Console), Ctrl+Shift+C (Element Picker)
//     if (event.ctrlKey && event.shiftKey && (event.keyCode === 73 || event.keyCode === 74 || event.keyCode === 67)) {
//         event.preventDefault();
//         return false;
//     }
//     // Ctrl+U (View Source)
//     if (event.ctrlKey && event.keyCode === 85) {
//         event.preventDefault();
//         return false;
//     }
// });

// // 3. Console Warning (Dahuka Style)
// const warningTitleStyle = 'color: #dc3545; font-size: 50px; font-weight: 800; font-family: "Montserrat", sans-serif;';
// const warningTextStyle = 'font-size: 18px; color: #111; font-family: "Montserrat", sans-serif; font-weight: 500;';
// const footerTextStyle = 'font-size: 14px; color: #666; font-style: italic;';

// setTimeout(() => {
//     console.clear();
//     console.log('%cDừng lại!', warningTitleStyle);
//     console.log('%cĐây là một tính năng của trình duyệt dành cho các nhà phát triển.', warningTextStyle);
//     console.log('%cNếu ai đó yêu cầu bạn sao chép và dán bất kỳ mã nào vào đây, đó rất có thể là một vụ lừa đảo nhằm đánh cắp thông tin tài khoản Dahuka của bạn.', warningTextStyle);
//     console.log('%cXây dựng bởi Dahuka Team — Nâng tầm sống khỏe chuẩn Nhật.', footerTextStyle);
// }, 1000);

(function () {
    const userMenu = document.getElementById('siteUserMenu');
    const userToggle = document.getElementById('siteUserToggle');
    if (userMenu && userToggle) {
        userToggle.addEventListener('click', function (event) {
            event.preventDefault();
            userMenu.classList.toggle('open');
        });
        document.addEventListener('click', function (event) {
            if (!userMenu.contains(event.target)) {
                userMenu.classList.remove('open');
            }
        });
    }

    const toastWrap = document.getElementById('siteToastWrap');
    
    function showToast(message, type = 'success') {
        if (!toastWrap) return;
        
        // Remove oldest toast if more than 3
        const activeToasts = toastWrap.querySelectorAll('.site-toast:not(.hide)');
        if (activeToasts.length >= 3) {
            const oldest = activeToasts[0];
            oldest.classList.add('hide');
            setTimeout(() => oldest.remove(), 400);
        }

        const toast = document.createElement('div');
        toast.className = `site-toast ${type}`;
        const iconClass = type === 'error' ? 'fa-times-circle' : 'fa-check-circle-o';
        
        toast.innerHTML = `
            <i class="fa ${iconClass}"></i>
            <span>${message}</span>
        `;
        
        toastWrap.appendChild(toast);
        updateToastStack();
        
        // Auto remove after 4s
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.add('hide');
                setTimeout(() => {
                    toast.remove();
                    updateToastStack();
                }, 400);
            }
        }, 4000);
    }

    function updateToastStack() {
        if (!toastWrap) return;
        const toasts = Array.from(toastWrap.querySelectorAll('.site-toast:not(.hide)'));
        toasts.forEach((t, i) => {
            // Stack from bottom up
            const offset = (toasts.length - 1 - i) * 10;
            const scale = 1 - (toasts.length - 1 - i) * 0.05;
            const opacity = 1 - (toasts.length - 1 - i) * 0.2;
            
            t.style.transform = `translateY(-${offset}px) scale(${scale})`;
            t.style.opacity = opacity;
            t.style.zIndex = i + 100;
        });
    }

    // Initialize existing toasts
    if (toastWrap) {
        updateToastStack();
        const existingToasts = toastWrap.querySelectorAll('.site-toast');
        existingToasts.forEach((toast, index) => {
            setTimeout(() => {
                toast.classList.add('hide');
                setTimeout(() => {
                    toast.remove();
                    updateToastStack();
                }, 400);
            }, 4000);
        });
    }

    // AJAX Cart Handling using Event Delegation
    document.addEventListener('submit', function(e) {
        const form = e.target.closest('.ajax-cart-form');
        if (!form) return;

        e.preventDefault();
        const formData = new FormData(form);
        const url = form.getAttribute('action');
        
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Cart update response:', data);
            if (data.status === 'success') {
                showToast(data.message);
                // Update cart count badge if exists
                const cartBadge = document.querySelector('.js-cart-badge');
                if (cartBadge && data.cart_count !== undefined) {
                    cartBadge.textContent = data.cart_count;
                    if (data.cart_count > 0) {
                        cartBadge.classList.remove('badge-hidden');
                    } else {
                        cartBadge.classList.add('badge-hidden');
                    }
                    
                    // Add pop effect
                    cartBadge.classList.remove('cart-badge-pop');
                    void cartBadge.offsetWidth; // Trigger reflow
                    cartBadge.classList.add('cart-badge-pop');
                }
            } else {
                showToast(data.message || 'Có lỗi xảy ra', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Không thể thêm vào giỏ hàng', 'error');
        });
    });

    const featurePopup = document.getElementById('featurePopup');
    const featurePopupClose = document.getElementById('featurePopupClose');
    const featurePopupTriggers = document.querySelectorAll('[data-feature-popup-trigger="guide-install"]');
    let featurePopupTimer = null;

    function closeFeaturePopup() {
        if (!featurePopup) return;
        featurePopup.classList.remove('is-open');
        featurePopup.setAttribute('aria-hidden', 'true');
        if (featurePopupTimer) {
            clearTimeout(featurePopupTimer);
            featurePopupTimer = null;
        }
    }

    function openFeaturePopup() {
        if (!featurePopup) return;
        featurePopup.classList.add('is-open');
        featurePopup.setAttribute('aria-hidden', 'false');
        if (featurePopupTimer) {
            clearTimeout(featurePopupTimer);
        }
        featurePopupTimer = setTimeout(closeFeaturePopup, 10000);
    }

    featurePopupTriggers.forEach(function (trigger) {
        trigger.addEventListener('click', function (event) {
            event.preventDefault();
            const popupImg = document.getElementById('featurePopupImg');
            if (popupImg) {
                popupImg.src = "/static/img/update_notice.png";
            }
            openFeaturePopup();
        });
    });

    if (featurePopupClose) {
        featurePopupClose.addEventListener('click', closeFeaturePopup);
    }

    if (featurePopup) {
        featurePopup.addEventListener('click', function (event) {
            if (event.target === featurePopup) {
                closeFeaturePopup();
            }
        });
    }

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            closeFeaturePopup();
        }
    });

    // Modal helpers
    window.openModal = function (id) {
        const modal = document.getElementById(id);
        if (modal) modal.classList.add('show');
    };

    window.closeModal = function (id) {
        const modal = document.getElementById(id);
        if (modal) modal.classList.remove('show');
    };

    // Close modals on clicking background or [data-close]
    document.addEventListener('click', (e) => {
        const closeBtn = e.target.closest('[data-close]');
        if (closeBtn) {
            closeModal(closeBtn.dataset.close);
        }
        
        const modal = e.target.closest('.modal');
        if (modal && e.target === modal) {
            modal.classList.remove('show');
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(m => m.classList.remove('show'));
        }
    });

    // Handle site headers
    const mainHeader = document.querySelector('.site-header');
    if (mainHeader) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                mainHeader.classList.add('scrolled');
            } else {
                mainHeader.classList.remove('scrolled');
            }
        });
    }
})();
