from odoo import http
from odoo.http import request
from datetime import datetime


class MedicalWebsite(http.Controller):

    @http.route('/medical', type='http', auth='public', website=True)
    def index(self, **kwargs):
        return request.render('medical_website.index', {})

    @http.route('/medical/rdv', type='http', auth='public', website=True)
    def prendre_rdv(self, **kwargs):
        doctors = request.env['medical.doctor'].sudo().search([('active', '=', True)])
        return request.render('medical_website.rdv', {
            'doctors': doctors,
            'error': kwargs.get('error'),
        })

    @http.route('/medical/rdv/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def submit_rdv(self, **kwargs):
        try:
            doctor_id = int(kwargs.get('doctor_id', 0))
            appointment_date = kwargs.get('appointment_date')
            first_name = kwargs.get('first_name', '').strip()
            last_name = kwargs.get('last_name', '').strip()
            phone = kwargs.get('phone', '').strip()

            if not doctor_id or not appointment_date or not first_name or not last_name:
                raise ValueError("Tous les champs obligatoires doivent être remplis.")

            # Vérifier que la date n'est pas dans le passé
            date_obj = datetime.strptime(appointment_date, '%Y-%m-%dT%H:%M')
            if date_obj < datetime.now():
                raise ValueError("Vous ne pouvez pas prendre un rendez-vous dans le passé.")

            # Chercher si le patient existe déjà
            patient = request.env['medical.patient'].sudo().search([
                ('first_name', 'ilike', first_name),
                ('last_name', 'ilike', last_name),
            ], limit=1)

            # Sinon le créer automatiquement
            if not patient:
                patient = request.env['medical.patient'].sudo().create({
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                })

            # Créer le RDV
            rdv = request.env['medical.appointment'].sudo().create({
                'doctor_id': doctor_id,
                'patient_id': patient.id,
                'appointment_date': date_obj,
                'state': 'draft',
            })

            # Rediriger vers la page de confirmation avec téléchargement PDF
            return request.redirect(f'/medical/rdv/confirmation/{rdv.id}')

        except Exception as e:
            doctors = request.env['medical.doctor'].sudo().search([('active', '=', True)])
            return request.render('medical_website.rdv', {
                'doctors': doctors,
                'error': str(e),
            })

    @http.route('/medical/rdv/confirmation/<int:rdv_id>', type='http', auth='public', website=True)
    def confirmation(self, rdv_id, **kwargs):
        rdv = request.env['medical.appointment'].sudo().browse(rdv_id)
        if not rdv.exists():
            return request.redirect('/medical/rdv')
        return request.render('medical_website.confirmation', {
            'rdv': rdv,
        })

    @http.route('/medical/rdv/pdf/<int:rdv_id>', type='http', auth='public', website=True)
    def download_pdf(self, rdv_id, **kwargs):
        rdv = request.env['medical.appointment'].sudo().browse(rdv_id)
        if not rdv.exists():
            return request.redirect('/medical/rdv')

        pdf_content, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'medical_appointment.report_appointment_document', [rdv_id]
        )
        filename = f"RDV_{rdv.name}.pdf"
        return request.make_response(
            pdf_content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{filename}"'),
            ]
        )