// === REVEAL ON SCROLL ===
(function() {
    function initReveal() {
        var elements = document.querySelectorAll('[data-reveal]');
        if (!elements.length) return;

        if ('IntersectionObserver' in window) {
            var observer = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        var delay = entry.target.getAttribute('data-reveal-delay') || 0;
                        setTimeout(function() {
                            entry.target.classList.add('is-revealed');
                        }, parseInt(delay));
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });

            elements.forEach(function(el) { observer.observe(el); });
        } else {
            elements.forEach(function(el) { el.classList.add('is-revealed'); });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initReveal);
    } else {
        initReveal();
    }
})();

function initDarkMode() {
    var isDark = localStorage.getItem('medicss_dark') === 'true';
    if (isDark) {
        document.body.classList.add('dark-mode');
        document.documentElement.classList.add('dark-mode');
    }

    // Créer le bouton
    var btn = document.createElement('button');
    btn.id = 'dark-mode-toggle';
    btn.className = 'dark-toggle-navbar';
    btn.innerHTML = isDark ? '☀️' : '🌙';
    btn.type = 'button';

    // Essayer de l'insérer dans la navbar
    var navbar = document.querySelector('#top_menu') ||
                 document.querySelector('.navbar-nav') ||
                 document.querySelector('nav .container');

    if (navbar) {
        var li = document.createElement('li');
        li.className = 'nav-item d-flex align-items-center';
        li.appendChild(btn);
        navbar.appendChild(li);
    } else {
        document.body.appendChild(btn);
    }

    btn.addEventListener('click', function() {
        isDark = !isDark;
        document.body.classList.toggle('dark-mode', isDark);
        document.documentElement.classList.toggle('dark-mode', isDark);
        localStorage.setItem('medicss_dark', isDark);
        btn.innerHTML = isDark ? '☀️' : '🌙';
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDarkMode);
} else {
    initDarkMode();
}