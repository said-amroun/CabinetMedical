from odoo import models, fields, api

class MedicalConsultation(models.Model):
    _name = 'medical.consultation'
    _description = 'Medical Consultation'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    appointment_id = fields.Many2one('medical.appointment', string='Appointment', required=True)
    
    patient_id = fields.Many2one('medical.patient', related='appointment_id.patient_id', string='Patient', readonly=True, store=True)
    doctor_id = fields.Many2one('medical.doctor', related='appointment_id.doctor_id', string='Doctor', readonly=True, store=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('done', 'Confirmé')
    ], string='Status', default='draft', required=True)
    consultation_date = fields.Datetime(string='Date de Consultation', readonly=True)
    
    symptoms = fields.Text(string='Symptoms')
    disease_id = fields.Many2one('medical.disease', string='Disease/Diagnosis')
    notes = fields.Text(string='Notes')
    
    prescription_line_ids = fields.One2many('medical.prescription.line', 'consultation_id', string='Prescriptions')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('medical.consultation') or 'New'
        return super(MedicalConsultation, self).create(vals_list)

    def action_confirm(self):
        for rec in self:
            rec.state = 'done'
            rec.consultation_date = fields.Datetime.now()


class MedicalPrescriptionLine(models.Model):
    _name = 'medical.prescription.line'
    _description = 'Prescription Line'

    consultation_id = fields.Many2one('medical.consultation', string='Consultation', ondelete='cascade')
    medication_id = fields.Many2one('medical.medication', string='Medication', required=True)
    dosage = fields.Char(string='Dosage', required=True)
    duration = fields.Char(string='Duration')
    note = fields.Char(string='Notes')
