from odoo import models, fields


class MedicalSpecialty(models.Model):
    _name = 'medical.specialty'
    _description = 'Spécialité Médicale'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')