from odoo import models, fields

class MedicalDisease(models.Model):
    _name = 'medical.disease'
    _description = 'Maladie / Diagnostic'

    name = fields.Char(string='Nom', required=True)
    description = fields.Text(string='Description')
