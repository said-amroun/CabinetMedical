from odoo import models, fields

class MedicalPatient(models.Model):
    _inherit = 'medical.patient'

    consultation_ids = fields.One2many('medical.consultation', 'patient_id', string='Consultations')
