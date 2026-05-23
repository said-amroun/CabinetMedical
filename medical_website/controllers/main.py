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
            email = kwargs.get('email', '').strip()

            if not doctor_id or not appointment_date or not first_name or not last_name:
                raise ValueError("Tous les champs obligatoires doivent être remplis.")

            date_obj = datetime.strptime(appointment_date, '%Y-%m-%dT%H:%M')
            if date_obj < datetime.now():
                raise ValueError("Vous ne pouvez pas prendre un rendez-vous dans le passé.")

            # Chercher si le patient existe déjà
            patient = request.env['medical.patient'].sudo().search([
                ('first_name', 'ilike', first_name),
                ('last_name', 'ilike', last_name),
            ], limit=1)

            # Sinon le créer
            if not patient:
                patient = request.env['medical.patient'].sudo().create({
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                    'email': email,
                })

            # Créer le RDV
            rdv = request.env['medical.appointment'].sudo().create({
                'doctor_id': doctor_id,
                'patient_id': patient.id,
                'appointment_date': date_obj,
                'state': 'draft',
            })

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
            'medical_website.report_appointment_document', [rdv_id]
        )
        filename = f"RDV_{rdv.name}.pdf"
        return request.make_response(
            pdf_content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{filename}"'),
            ]
        )

    @http.route('/medical/contact', type='http', auth='public', website=True)
    def contact(self, **kwargs):
        return request.render('medical_website.contact', {
            'success': kwargs.get('success'),
            'error': kwargs.get('error'),
        })

    @http.route('/medical/contact/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def contact_submit(self, **kwargs):
        try:
            name = kwargs.get('name', '').strip()
            email = kwargs.get('email', '').strip()
            subject = kwargs.get('subject', '').strip()
            message = kwargs.get('message', '').strip()

            if not name or not email or not message:
                raise ValueError("Tous les champs obligatoires doivent être remplis.")

            admin_email = request.env['ir.config_parameter'].sudo().get_param(
                'mail.catchall.alias') or 'admin@cabinet.com'

            mail_values = {
                'subject': f"[Contact site] {subject or 'Message du site web'}",
                'body_html': f"""
                        <p><strong>De :</strong> {name} ({email})</p>
                        <p><strong>Sujet :</strong> {subject or 'Sans sujet'}</p>
                        <p><strong>Message :</strong></p>
                        <p>{message}</p>
                    """,
                'email_from': email,
                'email_to': admin_email,
                'reply_to': email,
            }
            request.env['mail.mail'].sudo().create(mail_values).send()

            return request.redirect('/medical/contact?success=1')

        except Exception as e:
            return request.redirect(f'/medical/contact?error={str(e)}')

    @http.route('/medical/mes-rdv', type='http', auth='public', website=True)
    def mes_rdv(self, **kwargs):
        return request.render('medical_website.mes_rdv', {
            'rdvs': None,
            'searched': False,
            'error': kwargs.get('error'),
        })

    @http.route('/medical/mes-rdv/search', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def mes_rdv_search(self, **kwargs):
        first_name = kwargs.get('first_name', '').strip()
        last_name = kwargs.get('last_name', '').strip()
        reference = kwargs.get('reference', '').strip()

        try:
            if not first_name or not last_name or not reference:
                raise ValueError("Tous les champs sont obligatoires.")

            # Chercher le patient
            patient = request.env['medical.patient'].sudo().search([
                ('first_name', 'ilike', first_name),
                ('last_name', 'ilike', last_name),
            ], limit=1)

            if not patient:
                raise ValueError("Aucun patient trouvé avec ces informations.")

            # Chercher le RDV correspondant
            rdv = request.env['medical.appointment'].sudo().search([
                ('patient_id', '=', patient.id),
                ('name', '=', reference),
            ], limit=1)

            if not rdv:
                raise ValueError("Aucun rendez-vous trouvé avec cette référence.")

            # Chercher tous les RDV du patient
            rdvs = request.env['medical.appointment'].sudo().search([
                ('patient_id', '=', patient.id),
            ], order='appointment_date desc')

            return request.render('medical_website.mes_rdv', {
                'rdvs': rdvs,
                'patient': patient,
                'searched': True,
                'error': None,
            })

        except Exception as e:
            return request.render('medical_website.mes_rdv', {
                'rdvs': None,
                'searched': True,
                'error': str(e),
            })