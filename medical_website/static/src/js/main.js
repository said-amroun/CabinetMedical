(function() {
    function initFiltre() {
        var specialtySelect = document.getElementById('specialty_id');
        var doctorSelect = document.getElementById('doctor_id');
        var dateInput = document.getElementById('appointment_date');

        if (dateInput) {
            var now = new Date();
            now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
            dateInput.min = now.toISOString().slice(0, 16);
        }

        if (!specialtySelect || !doctorSelect) return;

        var allOptions = Array.from(doctorSelect.querySelectorAll('option'));

        specialtySelect.addEventListener('change', function () {
            var specialtyId = String(this.value);

            while (doctorSelect.options.length > 1) {
                doctorSelect.remove(1);
            }

            allOptions.forEach(function (option) {
                if (option.value === '' || option.value === null) return;
                var optSpecialty = String(option.getAttribute('data-specialty') || '');
                if (!specialtyId || specialtyId === '' || optSpecialty === specialtyId) {
                    doctorSelect.appendChild(option.cloneNode(true));
                }
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFiltre);
    } else {
        initFiltre();
    }

    // Backup pour Odoo qui charge le JS en asynchrone
    window.addEventListener('load', initFiltre);
})();
// Mode jour/nuit
function initDarkMode() {
    var isDark = localStorage.getItem('medicss_dark') === 'true';

    // Créer le bouton
    var btn = document.createElement('button');
    btn.id = 'dark-mode-toggle';
    btn.innerHTML = isDark ? '☀️' : '🌙';
    btn.title = isDark ? 'Mode jour' : 'Mode nuit';
    document.body.appendChild(btn);

    if (isDark) document.body.classList.add('dark-mode');

    btn.addEventListener('click', function() {
        isDark = !isDark;
        document.body.classList.toggle('dark-mode', isDark);
        localStorage.setItem('medicss_dark', isDark);
        btn.innerHTML = isDark ? '☀️' : '🌙';
        btn.title = isDark ? 'Mode jour' : 'Mode nuit';
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDarkMode);
} else {
    initDarkMode();
}