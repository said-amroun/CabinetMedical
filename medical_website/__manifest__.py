{
    'name': 'Medical Website',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Portail web pour la gestion médicale',
    'depends': ['website', 'medical_appointment'],  # ← dépend du module website
    'data': [
        'views/templates.xml',
        'views/website_menu.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'medical_website/static/src/css/style.css',
            'medical_website/static/src/js/main.js',
        ],
    },
    'installable': True,
    'application': False,
}
