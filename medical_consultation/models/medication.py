from odoo import models, fields

class MedicalMedication(models.Model):
    _name = 'medical.medication'
    _description = 'Medication'

    name = fields.Char(string='Name', required=True)
    active_ingredient = fields.Char(string='Active Ingredient')
