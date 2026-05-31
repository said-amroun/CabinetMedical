from odoo import models, fields

class MedicalMedication(models.Model):
    _name = 'medical.medication'
    _description = 'Médicament'

    name = fields.Char(string='Nom', required=True)
    active_ingredient = fields.Char(string='Principe Actif')
