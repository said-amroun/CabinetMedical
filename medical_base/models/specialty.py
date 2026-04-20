from odoo import models, fields


class MedicalSpecialty(models.Model):
    _name = 'medical.specialty'
    _description = 'Medical Specialty'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')