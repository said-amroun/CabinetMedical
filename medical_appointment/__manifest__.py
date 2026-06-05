{
    'name': 'Medical Appointment',
    'version': '1.0',
    'summary': 'Manage medical appointments',
    'description': 'Schedule and manage appointments between patients and doctors.',
    'author': 'DIB Syphax / AMROUN Said',
    'category': 'Healthcare',
    'depends': ['base', 'medical_base', 'mail'],
    'data': [
        'security/security_rules.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/dashboard_action.xml',
        'views/appointment_views.xml',
        'views/patient_views.xml',
        'views/medical_appointment_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'medical_appointment/static/src/js/dashboard.js',
            'medical_appointment/static/src/xml/dashboard.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
