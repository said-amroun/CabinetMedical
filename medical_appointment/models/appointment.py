from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError
from datetime import datetime, timedelta, time
import pytz


class MedicalAppointment(models.Model):
    _name = 'medical.appointment'
    _description = 'Rendez-vous Médical'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Référence', required=True, copy=False, readonly=True, default='New')
    patient_id = fields.Many2one('medical.patient', string='Patient', required=True)
    doctor_id = fields.Many2one('medical.doctor', string='Docteur', required=True)
    appointment_date = fields.Datetime(string='Date & Heure', required=True)
    duration = fields.Float(string='Durée (heures)', default=0.5)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string='Statut', default='draft', required=True)

    def _check_doctor_access(self, doctor_id):
        """Vérifie qu'un médecin ne crée/modifie que ses propres rendez-vous."""
        if self.env.user.has_group('medical_base.group_medical_doctor') \
                and not self.env.user.has_group('medical_base.group_medical_secretary') \
                and not self.env.user.has_group('medical_base.group_medical_admin'):
            my_doctor = self.env['medical.doctor'].search([('user_id', '=', self.env.uid)], limit=1)
            if my_doctor and doctor_id and doctor_id != my_doctor.id:
                raise AccessError("Accès refusé, vous pouvez créer seulement vos propres rendez-vous.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Vérifier que le médecin ne crée pas un rdv pour un autre médecin
            self._check_doctor_access(vals.get('doctor_id'))

            if vals.get('name', 'New') == 'New':
                # Get the patient's initials
                patient_id = vals.get('patient_id')
                initials = 'XX'
                if patient_id:
                    patient = self.env['medical.patient'].browse(patient_id)
                    if patient:
                        first_i = patient.first_name.strip()[0].upper() if patient.first_name and patient.first_name.strip() else 'X'
                        last_i = patient.last_name.strip()[0].upper() if patient.last_name and patient.last_name.strip() else 'X'
                        initials = f"{first_i}{last_i}"
                
                # Get the next sequence value
                seq = self.env['ir.sequence'].next_by_code('medical.appointment') or '00000'
                
                # Safely extract the numeric sequence part (in case the sequence definition has a prefix like 'APT/')
                seq_num = seq
                if '/' in seq:
                    seq_num = seq.split('/')[-1]
                elif '-' in seq:
                    seq_num = seq.split('-')[-1]
                
                vals['name'] = f"APT-{initials}/{seq_num}"
        return super(MedicalAppointment, self).create(vals_list)

    def write(self, vals):
        # Si le médecin tente de réassigner le rdv à un autre médecin
        if 'doctor_id' in vals:
            for rec in self:
                self._check_doctor_access(vals.get('doctor_id'))
        return super(MedicalAppointment, self).write(vals)


    @api.constrains('appointment_date')
    def _check_past_date(self):
        for record in self:
            if not record.appointment_date:
                continue
            if record.appointment_date < fields.Datetime.now():
                raise ValidationError("Vous ne pouvez pas prendre ou modifier un rendez-vous à une date et heure passées.")

    @api.constrains('doctor_id', 'appointment_date')
    def _check_doctor_availability(self):
        """Vérifie que le rendez-vous tombe sur un jour et créneau disponible du médecin."""
        user_tz = pytz.timezone(self.env.user.tz or 'Europe/Paris')
        for record in self:
            if not record.appointment_date or not record.doctor_id:
                continue

            # Convertir la date UTC en heure locale pour vérifier jour et créneau
            local_dt = pytz.utc.localize(record.appointment_date).astimezone(user_tz)
            day_of_week = str(local_dt.weekday())  # 0=Lundi .. 6=Dimanche
            local_hour = local_dt.hour + local_dt.minute / 60.0

            # Chercher la ligne de disponibilité du médecin pour ce jour
            availability = record.doctor_id.availability_ids.filtered(
                lambda a: a.day_of_week == day_of_week
            )

            day_names = {
                '0': 'Lundi', '1': 'Mardi', '2': 'Mercredi',
                '3': 'Jeudi', '4': 'Vendredi', '5': 'Samedi', '6': 'Dimanche',
            }
            day_name = day_names.get(day_of_week, day_of_week)

            if not availability:
                raise ValidationError(
                    f"Le Dr {record.doctor_id.name} n'est pas disponible le {day_name}."
                )

            # Vérifier que l'heure correspond à un créneau coché
            matching_slot = availability.slot_ids.filtered(
                lambda s: abs(s.start_hour - local_hour) < 0.01
            )
            if not matching_slot:
                hour_str = local_dt.strftime('%H:%M')
                raise ValidationError(
                    f"Le Dr {record.doctor_id.name} n'a pas de créneau disponible "
                    f"le {day_name} à {hour_str}."
                )

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

    @api.model
    def _cron_notify_tomorrow_appointments(self):
        # Retrieve target timezone
        tz_name = self.env.user.tz or 'Europe/Paris'
        user_tz = pytz.timezone(tz_name)

        # Calculate today and tomorrow local dates
        today_local = datetime.now(user_tz).date()
        tomorrow_local = today_local + timedelta(days=1)

        # Local bounds for tomorrow
        start_local = datetime.combine(tomorrow_local, time.min)
        end_local = datetime.combine(tomorrow_local, time.max)

        # Convert bounds to UTC for search query
        start_utc = user_tz.localize(start_local).astimezone(pytz.utc).replace(tzinfo=None)
        end_utc = user_tz.localize(end_local).astimezone(pytz.utc).replace(tzinfo=None)

        # Search for tomorrow's appointments
        appointments = self.search([
            ('appointment_date', '>=', start_utc),
            ('appointment_date', '<=', end_utc),
            ('state', '=', 'confirmed'),
            ('doctor_id.user_id', '!=', False),
        ])

        # Notify doctors
        for appointment in appointments:
            doctor_user = appointment.doctor_id.user_id
            
            # Formulate local time representation for the doctor
            appt_time_local = pytz.utc.localize(appointment.appointment_date).astimezone(user_tz)
            time_str = appt_time_local.strftime('%H:%M')

            # Avoid duplicating activities
            existing = self.env['mail.activity'].search([
                ('res_model', '=', 'medical.appointment'),
                ('res_id', '=', appointment.id),
                ('user_id', '=', doctor_user.id),
            ], limit=1)

            if not existing:
                appointment.activity_schedule(
                    act_type_xmlid='mail.mail_activity_data_todo',
                    date_deadline=tomorrow_local,
                    summary=f"Consultation demain : {appointment.patient_id.name}",
                    note=f"Rappel: Vous avez une consultation demain à {time_str} avec le patient {appointment.patient_id.name}.",
                    user_id=doctor_user.id
                )
