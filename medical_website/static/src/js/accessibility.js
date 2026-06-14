(function() {
    'use strict';

    // ========== INJECTION DU BOUTON ET DU PANNEAU ==========
    function injectAccessibilityUI() {
        if (document.getElementById('a11y-fab')) return;

        // Bouton flottant
        var fab = document.createElement('button');
        fab.id = 'a11y-fab';
        fab.setAttribute('aria-label', "Options d'accessibilité");
        fab.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:26px;height:26px;"><circle cx="12" cy="4" r="2"/><path d="M19 13v-2c0-1.1-.9-2-2-2H7c-1.1 0-2 .9-2 2v2"/><path d="M12 9v6"/><path d="M9 21l3-6 3 6"/></svg>';
        document.body.appendChild(fab);

        // Panneau
        var panel = document.createElement('div');
        panel.id = 'a11y-panel';
        panel.innerHTML = '' +
            '<div class="a11y-panel-header">' +
                '<h3>Accessibilité</h3>' +
                '<button class="a11y-close" aria-label="Fermer">×</button>' +
            '</div>' +
            '<div class="a11y-panel-body">' +
                '<div class="a11y-section">' +
                    '<p class="a11y-label">Taille du texte</p>' +
                    '<div class="a11y-btn-group" data-setting="fontSize">' +
                        '<button data-value="normal" class="a11y-btn active">A</button>' +
                        '<button data-value="large" class="a11y-btn">A+</button>' +
                        '<button data-value="xlarge" class="a11y-btn">A++</button>' +
                    '</div>' +
                '</div>' +
                '<div class="a11y-section">' +
                    '<p class="a11y-label">Contraste élevé</p>' +
                    '<label class="a11y-toggle">' +
                        '<input type="checkbox" data-setting="highContrast"/>' +
                        '<span class="a11y-slider"></span>' +
                    '</label>' +
                '</div>' +
                '<div class="a11y-section">' +
                    '<p class="a11y-label">Animations réduites</p>' +
                    '<label class="a11y-toggle">' +
                        '<input type="checkbox" data-setting="reduceMotion"/>' +
                        '<span class="a11y-slider"></span>' +
                    '</label>' +
                '</div>' +
                '<div class="a11y-section">' +
                    '<p class="a11y-label">Soulignement des liens</p>' +
                    '<label class="a11y-toggle">' +
                        '<input type="checkbox" data-setting="underlineLinks"/>' +
                        '<span class="a11y-slider"></span>' +
                    '</label>' +
                '</div>' +
                '<button class="a11y-reset">Réinitialiser</button>' +
            '</div>';
        document.body.appendChild(panel);

        // Events
        fab.addEventListener('click', function() {
            panel.classList.toggle('a11y-open');
        });
        panel.querySelector('.a11y-close').addEventListener('click', function() {
            panel.classList.remove('a11y-open');
        });

        // Click sur boutons taille
        panel.querySelectorAll('[data-setting="fontSize"] button').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var value = btn.getAttribute('data-value');
                applySetting('fontSize', value);
                save('fontSize', value);
                panel.querySelectorAll('[data-setting="fontSize"] button').forEach(function(b) {
                    b.classList.toggle('active', b.getAttribute('data-value') === value);
                });
            });
        });

        // Toggles
        panel.querySelectorAll('input[type="checkbox"][data-setting]').forEach(function(input) {
            input.addEventListener('change', function() {
                var setting = input.getAttribute('data-setting');
                applySetting(setting, input.checked);
                save(setting, input.checked);
            });
        });

        // Reset
        panel.querySelector('.a11y-reset').addEventListener('click', function() {
            localStorage.removeItem('a11y');
            location.reload();
        });
    }

    // ========== APPLICATION DES PRÉFÉRENCES ==========
    function applySetting(name, value) {
        var html = document.documentElement;
        if (name === 'fontSize') {
            html.classList.remove('a11y-font-large', 'a11y-font-xlarge');
            if (value === 'large') html.classList.add('a11y-font-large');
            if (value === 'xlarge') html.classList.add('a11y-font-xlarge');
        } else if (name === 'highContrast') {
            html.classList.toggle('a11y-high-contrast', value);
        } else if (name === 'reduceMotion') {
            html.classList.toggle('a11y-reduce-motion', value);
        } else if (name === 'underlineLinks') {
            html.classList.toggle('a11y-underline-links', value);
        }
    }

    function save(name, value) {
        var settings = JSON.parse(localStorage.getItem('a11y') || '{}');
        settings[name] = value;
        localStorage.setItem('a11y', JSON.stringify(settings));
    }

    function loadSettings() {
        var settings = JSON.parse(localStorage.getItem('a11y') || '{}');
        Object.keys(settings).forEach(function(key) {
            applySetting(key, settings[key]);
        });
        // Met à jour l'UI au chargement
        setTimeout(function() {
            var panel = document.getElementById('a11y-panel');
            if (!panel) return;
            if (settings.fontSize) {
                panel.querySelectorAll('[data-setting="fontSize"] button').forEach(function(b) {
                    b.classList.toggle('active', b.getAttribute('data-value') === settings.fontSize);
                });
            }
            ['highContrast', 'reduceMotion', 'underlineLinks'].forEach(function(s) {
                if (settings[s]) {
                    var input = panel.querySelector('input[data-setting="' + s + '"]');
                    if (input) input.checked = true;
                }
            });
        }, 50);
    }

    // ========== INIT ==========
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            loadSettings();
            injectAccessibilityUI();
            loadSettings();
        });
    } else {
        loadSettings();
        injectAccessibilityUI();
        loadSettings();
    }
})();