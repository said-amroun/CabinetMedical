from odoo import models, fields, api

class MedicalConsultation(models.Model):
    _name = 'medical.consultation'
    _description = 'Medical Consultation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    appointment_id = fields.Many2one('medical.appointment', string='Rendez-vous', required=True, domain=[('state', '!=', 'done')])
    
    patient_id = fields.Many2one('medical.patient', related='appointment_id.patient_id', string='Patient', readonly=True, store=True)
    doctor_id = fields.Many2one('medical.doctor', related='appointment_id.doctor_id', string='Docteur', readonly=True, store=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('done', 'Confirmé')
    ], string='Status', default='draft', required=True)
    consultation_date = fields.Datetime(string='Date de Consultation', readonly=True)
    
    symptoms = fields.Text(string='Symptômes')
    disease_id = fields.Many2one('medical.disease', string='Maladie/Diagnostic')
    notes = fields.Text(string='Notes')
    
    prescription_line_ids = fields.One2many('medical.prescription.line', 'consultation_id', string='Ordonnances')
    document_ids = fields.One2many('medical.consultation.document', 'consultation_id', string='Attestations / Justificatifs')
    city = fields.Char(string='Ville', default='Aix-En-Provence')
    treatment_summary = fields.Text(string='Traitement', compute='_compute_treatment_summary')

    @api.depends('prescription_line_ids.medication_id', 'prescription_line_ids.dosage')
    def _compute_treatment_summary(self):
        for rec in self:
            if rec.prescription_line_ids:
                rec.treatment_summary = ', '.join([f"{p.medication_id.name} ({p.dosage})" for p in rec.prescription_line_ids if p.medication_id])
            else:
                rec.treatment_summary = ''

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
            if rec.appointment_id:
                rec.appointment_id.action_done()


class MedicalPrescriptionLine(models.Model):
    _name = 'medical.prescription.line'
    _description = 'Prescription Line'

    consultation_id = fields.Many2one('medical.consultation', string='Consultation', ondelete='cascade')
    medication_id = fields.Many2one('medical.medication', string='Médicament', required=True)
    dosage = fields.Char(string='Posologie', required=True)
    duration = fields.Char(string='Durée')
    note = fields.Char(string='Notes')


class MedicalConsultationDocument(models.Model):
    _name = 'medical.consultation.document'
    _description = 'Attestation et Document Médical'

    consultation_id = fields.Many2one('medical.consultation', string='Consultation', ondelete='cascade')
    title = fields.Char(string='Titre du document', required=True)
    content = fields.Text(string='Contenu du document', required=True)
