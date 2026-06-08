from odoo import models, fields


class MedicalTimeSlot(models.Model):
    _name = 'medical.time.slot'
    _description = 'Créneau horaire de 30 minutes'
    _order = 'start_hour'

    name = fields.Char(string='Créneau', required=True)
    start_hour = fields.Float(string='Heure de début', required=True)
    end_hour = fields.Float(string='Heure de fin', required=True)
