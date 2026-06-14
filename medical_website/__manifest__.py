{
    'name': 'Medical Website',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Portail web pour la gestion médicale',
    'description': 'Site vitrine du cabinet médical avec prise de rendez-vous en ligne.',
    'author': 'DIB Syphax / AMROUN Said',
    'depends': ['website', 'medical_appointment', 'mail'],
    'data': [
        'reports/appointment_report.xml',
        'views/templates.xml',
        'views/website_menu.xml',
        'views/dark_mode.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'medical_website/static/src/css/style.css',
            'medical_website/static/src/js/main.js',
            'medical_website/static/src/js/accessibility.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}