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
    if (toastWrap) {
        setTimeout(() => {
            toastWrap.style.opacity = '0';
            toastWrap.style.transition = 'opacity 1s ease';
            setTimeout(() => toastWrap.remove(), 1000);
        }, 5000);
    }

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
