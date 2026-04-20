{
    'name': 'Medical Base',
    'version': '1.0',
    'summary': 'Base module for medical cabinet management',
    'description': 'Manage doctors, patients and specialties.',
    'author': 'DIB Syphax / AMROUN Said',
    'category': 'Healthcare',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/medical_menu.xml',
        'views/specialty_views.xml',
        'views/doctor_views.xml',
        'views/patient_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}