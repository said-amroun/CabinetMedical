from odoo import models, fields

class MedicalDisease(models.Model):
    _name = 'medical.disease'
    _description = 'Disease / Diagnosis'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
