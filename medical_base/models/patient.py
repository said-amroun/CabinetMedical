from odoo import models, fields, api


class MedicalPatient(models.Model):
    _name = 'medical.patient'
    _description = 'Patient'

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    name = fields.Char(string='Full Name', compute='_compute_name', store=True)
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age', store=False)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    user_id = fields.Many2one('res.users', string='Utilisateur lié', ondelete='set null')

    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for record in self:
            first = record.first_name or ''
            last = record.last_name or ''
            record.name = f"{first} {last}".strip()

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = fields.Date.today()
                delta = today - record.birth_date
                record.age = delta.days // 365
            else:
                record.age = 0