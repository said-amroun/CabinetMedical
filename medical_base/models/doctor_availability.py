from odoo import models, fields, api


DAYS_SELECTION = [
    ('0', 'Lundi'),
    ('1', 'Mardi'),
    ('2', 'Mercredi'),
    ('3', 'Jeudi'),
    ('4', 'Vendredi'),
    ('5', 'Samedi'),
    ('6', 'Dimanche'),
]


class MedicalDoctorAvailability(models.Model):
    _name = 'medical.doctor.availability'
    _description = 'Disponibilité du médecin par jour'
    _order = 'day_of_week'

    doctor_id = fields.Many2one(
        'medical.doctor',
        string='Médecin',
        required=True,
        ondelete='cascade',
    )
    day_of_week = fields.Selection(
        DAYS_SELECTION,
        string='Jour',
        required=True,
    )
    slot_ids = fields.Many2many(
        'medical.time.slot',
        'doctor_availability_slot_rel',
        'availability_id',
        'slot_id',
        string='Créneaux disponibles',
    )

    _sql_constraints = [
        ('unique_doctor_day', 'UNIQUE(doctor_id, day_of_week)',
         'Un médecin ne peut avoir qu\'une seule ligne de disponibilité par jour.'),
    ]
