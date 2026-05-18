from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
import pytz


class MedicalAppointment(models.Model):
    _name = 'medical.appointment'
    _description = 'Medical Appointment'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    patient_id = fields.Many2one('medical.patient', string='Patient', required=True)
    doctor_id = fields.Many2one('medical.doctor', string='Doctor', required=True)
    appointment_date = fields.Datetime(string='Date & Time', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('medical.appointment') or 'New'
        return super(MedicalAppointment, self).create(vals_list)

    @api.constrains('appointment_date')
    def _check_past_date(self):
        for record in self:
            if not record.appointment_date:
                continue
            if record.appointment_date < fields.Datetime.now():
                raise ValidationError("Vous ne pouvez pas prendre ou modifier un rendez-vous à une date et heure passées.")

    @api.constrains('appointment_date')
    def _check_working_hours(self):
        for record in self:
            if not record.appointment_date:
                continue
            
            user_tz = pytz.timezone(self.env.user.tz or 'UTC')
            local_time = pytz.utc.localize(record.appointment_date).astimezone(user_tz)
            hour = local_time.hour
            
            if not (8 <= hour < 17):
                raise ValidationError("Les rendez-vous doivent avoir lieu entre 08:00 et 17:00.")

    @api.constrains('doctor_id', 'appointment_date')
    def _check_overlap(self):
        for record in self:
            if not record.appointment_date:
                continue
                
            start_date = record.appointment_date
            end_date = start_date + timedelta(minutes=30)
            
            domain = [
                ('doctor_id', '=', record.doctor_id.id),
                ('id', '!=', record.id),
                ('state', '!=', 'cancelled')
            ]
            
            overlapping = self.search(domain).filtered(
                lambda app: app.appointment_date < end_date and (app.appointment_date + timedelta(minutes=30)) > start_date
            )
            if overlapping:
                raise ValidationError("Le médecin a déjà un rendez-vous (de 30 min) à cette heure.")

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
