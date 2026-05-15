from odoo import models, fields, api


class MedicalPatient(models.Model):
    _inherit = 'medical.patient'

    appointment_ids = fields.One2many('medical.appointment', 'patient_id', string='Rendez-vous')
    appointment_count = fields.Integer(
        string='Nombre de rendez-vous',
        compute='_compute_appointment_count',
        store=False,
    )

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for patient in self:
            patient.appointment_count = len(patient.appointment_ids)

    def action_view_appointments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rendez-vous',
            'res_model': 'medical.appointment',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }
