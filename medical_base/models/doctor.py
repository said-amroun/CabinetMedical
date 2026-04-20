from odoo import models, fields, api


class MedicalDoctor(models.Model):
    _name = 'medical.doctor'
    _description = 'Doctor'

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    name = fields.Char(string='Full Name', compute='_compute_name', store=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    specialty_id = fields.Many2one('medical.specialty', string='Specialty')
    bio = fields.Text(string='Biography')
    active = fields.Boolean(string='Active', default=True)

    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for record in self:
            first = record.first_name or ''
            last = record.last_name or ''
            record.name = f"{first} {last}".strip()