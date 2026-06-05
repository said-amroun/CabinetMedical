from odoo import models, fields, api


class MedicalPatient(models.Model):
    _inherit = 'medical.patient'

    consultation_ids = fields.One2many('medical.consultation', 'patient_id', string='Consultations')

    consultation_count = fields.Integer(
        string='Consultations',
        compute='_compute_consultation_count',
    )

    @api.depends('consultation_ids')
    def _compute_consultation_count(self):
        for patient in self:
            patient.consultation_count = self.env['medical.consultation'].search_count([
                ('patient_id', '=', patient.id),
            ])

    def action_view_consultations(self):
        self.ensure_one()
        return {
            'name': 'Suivi Médical',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.consultation',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }
