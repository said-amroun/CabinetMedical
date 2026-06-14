from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError

class MedicalDoctor(models.Model):
    _inherit = 'medical.doctor'

    street = fields.Char(string='Adresse (Rue)', default='2 Rue Jean Andreani')
    zip = fields.Char(string='Code Postal', default='13090')
    city = fields.Char(string='Ville', default='Aix-En-Provence')


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
        ('done', 'Confirmé'),
        ('locked', 'Verrouillé')
    ], string='Status', default='draft', required=True)
    consultation_date = fields.Datetime(string='Date de Consultation', readonly=True)
    
    symptoms = fields.Text(string='Symptômes')
    disease_id = fields.Many2one('medical.disease', string='Maladie/Diagnostic')
    notes = fields.Text(string='Notes')
    
    prescription_line_ids = fields.One2many('medical.prescription.line', 'consultation_id', string='Ordonnances')
    document_ids = fields.One2many('medical.consultation.document', 'consultation_id', string='Attestations / Justificatifs')

    # Préconsultation
    weight = fields.Float(string='Poids (kg)')
    height = fields.Float(string='Taille (cm)')
    preconsultation_care = fields.Text(string='Soins administrés en préconsultation')
    preconsultation_notes = fields.Text(string='Notes de préconsultation')

    treatment_summary = fields.Text(string='Traitement', compute='_compute_treatment_summary')

    @api.depends('prescription_line_ids.medication_id', 'prescription_line_ids.dosage')
    def _compute_treatment_summary(self):
        for rec in self:
            med_lines = rec.prescription_line_ids.filtered(lambda l: l.line_type == 'medication' and l.medication_id)
            if med_lines:
                rec.treatment_summary = ', '.join([f"{p.medication_id.name} ({p.dosage})" for p in med_lines])
            else:
                rec.treatment_summary = ''

    def _check_doctor_access(self, appointment_id):
        """Vérifie qu'un médecin ne crée/modifie que ses propres consultations."""
        if self.env.user.has_group('medical_base.group_medical_doctor') \
                and not self.env.user.has_group('medical_base.group_medical_secretary') \
                and not self.env.user.has_group('medical_base.group_medical_admin'):
            if appointment_id:
                appointment = self.env['medical.appointment'].browse(appointment_id)
                if appointment.doctor_id and appointment.doctor_id.user_id \
                        and appointment.doctor_id.user_id.id != self.env.uid:
                    raise AccessError("Accès refusé, vous pouvez créer seulement vos propres consultations.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._check_doctor_access(vals.get('appointment_id'))
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('medical.consultation') or 'New'
        return super(MedicalConsultation, self).create(vals_list)

    def write(self, vals):
        for rec in self:
            if rec.state == 'locked' and not self.env.user.has_group('medical_base.group_medical_admin'):
                raise AccessError("Cette consultation est verrouillée. Seul un administrateur peut la modifier.")
        if 'appointment_id' in vals:
            for rec in self:
                self._check_doctor_access(vals.get('appointment_id'))
        return super(MedicalConsultation, self).write(vals)

    def action_confirm(self):
        for rec in self:
            rec.state = 'done'
            rec.consultation_date = fields.Datetime.now()
            if rec.appointment_id:
                rec.appointment_id.action_done()

    def action_lock(self):
        for rec in self:
            rec.state = 'locked'


class MedicalPrescriptionLine(models.Model):
    _name = 'medical.prescription.line'
    _description = 'Prescription Line'

    consultation_id = fields.Many2one('medical.consultation', string='Consultation', ondelete='cascade')
    to_print = fields.Boolean(string="À imprimer", default=True)
    line_type = fields.Selection([
        ('medication', 'Médicament'),
        ('custom', 'Autre (Soin, Examen...)')
    ], string='Type de ligne', default='medication', required=True)
    
    medication_id = fields.Many2one('medical.medication', string='Médicament')
    dosage = fields.Char(string='Posologie')
    duration = fields.Char(string='Durée')
    note = fields.Char(string='Notes')

    custom_title = fields.Char(string='Titre / Nom')
    custom_text = fields.Text(string='Description / Instructions')

    @api.constrains('line_type', 'medication_id', 'dosage', 'custom_title')
    def _check_required_fields(self):
        for rec in self:
            if rec.line_type == 'medication':
                if not rec.medication_id:
                    raise ValidationError("Le médicament est obligatoire pour les lignes de type médicament.")
                if not rec.dosage:
                    raise ValidationError("La posologie est obligatoire pour les lignes de type médicament.")
            elif rec.line_type == 'custom':
                if not rec.custom_title:
                    raise ValidationError("Le titre/nom est obligatoire pour les lignes personnalisées.")


class MedicalConsultationDocument(models.Model):
    _name = 'medical.consultation.document'
    _description = 'Attestation et Document Médical'

    consultation_id = fields.Many2one('medical.consultation', string='Consultation', ondelete='cascade')
    template_id = fields.Many2one('medical.attestation.template', string='Modèle d\'attestation')
    title = fields.Char(string='Titre du document', required=True)
    content = fields.Text(string='Contenu du document', required=True)
    city = fields.Char(string='Ville', default='Aix-En-Provence')
    document_date = fields.Date(string='Date du document', default=fields.Date.today)

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.title = self.template_id.title
            if self.template_id.content:
                self.content = self.template_id.content

