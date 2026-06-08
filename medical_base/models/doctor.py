from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import email_normalize
import re

try:
    import phonenumbers
except ImportError:
    phonenumbers = None

PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\.\(\)]+$")
NAME_REGEX = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s\-']+$")


class MedicalDoctor(models.Model):
    _name = 'medical.doctor'
    _description = 'Doctor'

    first_name = fields.Char(string='Prénom', required=True)
    last_name = fields.Char(string='Nom', required=True)
    name = fields.Char(string='Nom Complet', compute='_compute_name', store=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Téléphone')
    specialty_id = fields.Many2one('medical.specialty', string='Spécialité')
    bio = fields.Text(string='Biographie')
    user_id = fields.Many2one('res.users', string='Utilisateur Odoo', help='Lié à l\'utilisateur du système')
    availability_ids = fields.One2many(
        'medical.doctor.availability',
        'doctor_id',
        string='Disponibilités',
    )

    @api.model_create_multi
    def create(self, vals_list):
        doctors = super().create(vals_list)
        # Créer les disponibilités par défaut (Lundi-Vendredi, tous les créneaux)
        all_slots = self.env['medical.time.slot'].search([])
        if all_slots:
            for doctor in doctors:
                if not doctor.availability_ids:
                    avail_vals = []
                    for day in range(5):  # 0=Lundi .. 4=Vendredi
                        avail_vals.append({
                            'doctor_id': doctor.id,
                            'day_of_week': str(day),
                            'slot_ids': [(6, 0, all_slots.ids)],
                        })
                    self.env['medical.doctor.availability'].create(avail_vals)
        return doctors

    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for record in self:
            first = record.first_name or ''
            last = record.last_name or ''
            record.name = f"{first} {last}".strip()

    @api.constrains('first_name', 'last_name')
    def _check_name(self):
        for record in self:
            if record.first_name and not NAME_REGEX.match(record.first_name):
                raise ValidationError("Le prénom '%s' ne doit contenir que des lettres (A-Z, accents), espaces, tirets ou apostrophes." % record.first_name)
            if record.last_name and not NAME_REGEX.match(record.last_name):
                raise ValidationError("Le nom '%s' ne doit contenir que des lettres (A-Z, accents), espaces, tirets ou apostrophes." % record.last_name)

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                normalized = email_normalize(record.email)
                if not normalized or not re.match(r"^[^@]+@[^@]+\.[a-zA-Z]{2,}$", normalized):
                    raise ValidationError("L'adresse email '%s' n'est pas valide (ex: docteur@domaine.com)." % record.email)

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone:
                if phonenumbers:
                    country_code = record.env.company.country_id.code or None
                    try:
                        phone_nbr = phonenumbers.parse(record.phone, country_code)
                        if not phonenumbers.is_valid_number(phone_nbr):
                            raise ValidationError("Le numéro de téléphone '%s' n'est pas valide." % record.phone)
                    except Exception:
                        raise ValidationError("Le numéro de téléphone '%s' n'est pas valide." % record.phone)
                else:
                    if not PHONE_REGEX.match(record.phone) or sum(c.isdigit() for c in record.phone) < 8:
                        raise ValidationError("Le numéro de téléphone '%s' n'est pas valide (minimum 8 chiffres attendus)." % record.phone)