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
// === PAGE RDV : sélection de date + créneaux ===
(function() {
    function initRdvPicker() {
        var dateInput = document.getElementById('rdv-date-input');
        var dateLabel = document.getElementById('rdv-date-label');
        var slotsContainer = document.getElementById('rdv-slots-container');
        var selectedText = document.getElementById('rdv-selected-text');
        var dateInputHidden = document.getElementById('appointment_date_input');
        var formSection = document.getElementById('rdv-form-section');
        if (!dateInput) return;

        var days = ['dimanche','lundi','mardi','mercredi','jeudi','vendredi','samedi'];
        var months = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];

        function renderSlots() {
            var dateStr = dateInput.value;
            if (!dateStr) return;
            var parts = dateStr.split('-');
            var d = new Date(parseInt(parts[0]), parseInt(parts[1])-1, parseInt(parts[2]));
            var today = new Date();
            today.setHours(0,0,0,0);

            dateLabel.textContent = days[d.getDay()].charAt(0).toUpperCase() + days[d.getDay()].slice(1) + ' ' + d.getDate() + ' ' + months[d.getMonth()] + ' ' + d.getFullYear();

            if (d.getDay() === 0) {
                slotsContainer.innerHTML = '<p class="rdv-no-slots">Le cabinet est fermé le dimanche. Sélectionnez un autre jour.</p>';
                return;
            }

            var html = '';
            var now = new Date();
            var isToday = (d.getTime() === today.getTime());

            for (var h = 8; h < 17; h++) {
                for (var m = 0; m < 60; m += 30) {
                    var slotDate = new Date(d);
                    slotDate.setHours(h, m, 0, 0);
                    if (isToday && slotDate < now) continue;
                    var hh = String(h).padStart(2,'0');
                    var mm = String(m).padStart(2,'0');
                    var val = parts[0]+'-'+parts[1]+'-'+parts[2]+'T'+hh+':'+mm;
                    var lbl = days[d.getDay()] + ' ' + d.getDate() + ' ' + months[d.getMonth()] + ' à ' + hh + ':' + mm;
                    html += '<button type="button" class="rdv-slot-btn" data-value="'+val+'" data-label="'+lbl+'">'+hh+':'+mm+'</button>';
                }
            }
            if (!html) html = '<p class="rdv-no-slots">Aucun créneau disponible ce jour.</p>';
            slotsContainer.innerHTML = html;

            slotsContainer.querySelectorAll('.rdv-slot-btn').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    slotsContainer.querySelectorAll('.rdv-slot-btn').forEach(function(b) { b.classList.remove('selected'); });
                    btn.classList.add('selected');
                    dateInputHidden.value = btn.getAttribute('data-value');
                    selectedText.textContent = btn.getAttribute('data-label');
                    formSection.style.display = 'block';
                    setTimeout(function() { formSection.scrollIntoView({behavior:'smooth', block:'start'}); }, 100);
                });
            });
        }

        dateInput.addEventListener('change', renderSlots);
        renderSlots();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initRdvPicker);
    } else {
        initRdvPicker();
    }
})();