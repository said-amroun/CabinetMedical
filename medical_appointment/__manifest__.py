{
    'name': 'Medical Appointment',
    'version': '1.0',
    'summary': 'Manage medical appointments',
    'description': 'Schedule and manage appointments between patients and doctors.',
    'author': 'DIB Syphax / AMROUN Said',
    'category': 'Healthcare',
    'depends': ['base', 'medical_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/appointment_views.xml',
        'views/medical_appointment_menu.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
