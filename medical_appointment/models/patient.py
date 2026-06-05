from odoo import models, fields, api


class MedicalPatient(models.Model):
    _inherit = 'medical.patient'

    appointment_ids = fields.One2many(
        'medical.appointment', 'patient_id', string='Rendez-vous')

    appointment_not_done_count = fields.Integer(
        string='RDV non terminés',
        compute='_compute_appointment_not_done_count',
    )

    @api.depends('appointment_ids', 'appointment_ids.state')
    def _compute_appointment_not_done_count(self):
        for patient in self:
            patient.appointment_not_done_count = self.env['medical.appointment'].search_count([
                ('patient_id', '=', patient.id),
                ('state', 'not in', ['done', 'cancelled']),
            ])

    def action_view_appointments_not_done(self):
        self.ensure_one()
        return {
            'name': 'Rendez-vous en cours',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.appointment',
            'view_mode': 'list,calendar,form',
            'domain': [
                ('patient_id', '=', self.id),
                ('state', 'not in', ['done', 'cancelled']),
            ],
            'context': {'default_patient_id': self.id},
        }
