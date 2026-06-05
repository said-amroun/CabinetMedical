from odoo import http
from odoo.http import request
from datetime import datetime


class MedicalWebsite(http.Controller):
    @http.route('/', type='http', auth='public', website=True, sitemap=False)
    def homepage(self, **kwargs):
        return request.redirect('/medical')

    @http.route('/medical', type='http', auth='public', website=True)
    def index(self, **kwargs):
        doctor = request.env['medical.doctor'].sudo().search([], limit=1)
        return request.render('medical_website.index', {
            'featured_doctor': doctor,
        })

    @http.route('/medical/medecins', type='http', auth='public', website=True)
    def medecins(self, **kwargs):
        doctors = request.env['medical.doctor'].sudo().search([])
        return request.render('medical_website.medecins', {
            'doctors': doctors,
        })

    @http.route('/medical/rdv', type='http', auth='public', website=True)
    def prendre_rdv(self, **kwargs):
        doctor_id = kwargs.get('doctor_id')
        if not doctor_id:
            return request.redirect('/medical/medecins')
        selected_doctor = request.env['medical.doctor'].sudo().browse(int(doctor_id))
        return request.render('medical_website.rdv', {
            'selected_doctor': selected_doctor,
            'error': kwargs.get('error'),
        })

    @http.route('/medical/rdv/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def submit_rdv(self, **kwargs):
        doctors = request.env['medical.doctor'].sudo().search([])
        try:
            doctor_id = int(kwargs.get('doctor_id', 0))
            appointment_date = kwargs.get('appointment_date')
            first_name = kwargs.get('first_name', '').strip()
            last_name = kwargs.get('last_name', '').strip()
            phone = kwargs.get('phone', '').strip()
            email = kwargs.get('email', '').strip()

            if not doctor_id or not appointment_date or not first_name or not last_name:
                raise ValueError("Tous les champs obligatoires doivent être remplis.")

            # Heure LOCALE choisie par l'utilisateur
            date_local = datetime.strptime(appointment_date, '%Y-%m-%dT%H:%M')

            # Validations sur l'heure LOCALE (avant conversion UTC)
            if not (8 <= date_local.hour < 17):
                raise ValueError("Les RDV sont disponibles uniquement entre 08h00 et 17h00.")

            if date_local.weekday() >= 5:
                raise ValueError("Les RDV ne sont pas disponibles le weekend.")

            # Conversion en UTC pour stockage
            import pytz
            user_tz = pytz.timezone('Europe/Paris')
            date_utc = user_tz.localize(date_local).astimezone(pytz.utc).replace(tzinfo=None)

            if date_utc < datetime.utcnow():
                raise ValueError("La date choisie est déjà passée.")

            patient = request.env['medical.patient'].sudo().search([
                ('first_name', 'ilike', first_name),
                ('last_name', 'ilike', last_name),
            ], limit=1)

            if not patient:
                patient = request.env['medical.patient'].sudo().create({
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                    'email': email,
                })

            # Création du RDV
            rdv = request.env['medical.appointment'].sudo().create({
                'doctor_id': doctor_id,
                'patient_id': patient.id,
                'appointment_date': date_utc,
                'state': 'draft',
            })
            rdv.flush_recordset()

            return request.redirect(f'/medical/rdv/confirmation/{rdv.id}')

        except Exception as e:

            request.env.cr.rollback()

            selected_doctor = None
            doctor_id = kwargs.get('doctor_id')
            if doctor_id:
                selected_doctor = request.env['medical.doctor'].sudo().browse(int(doctor_id))

            # Nettoyer le message d'erreur
            error_msg = str(e)
            if 'ValidationError' in error_msg:
                error_msg = error_msg.split('\n')[-1]

            return request.render('medical_website.rdv', {
                'doctors': doctors,
                'selected_doctor': selected_doctor,
                'error': error_msg,
                'form_data': {
                    'first_name': kwargs.get('first_name', ''),
                    'last_name': kwargs.get('last_name', ''),
                    'phone': kwargs.get('phone', ''),
                    'email': kwargs.get('email', ''),
                    'doctor_id': kwargs.get('doctor_id', ''),
                    'appointment_date': kwargs.get('appointment_date', ''),
                }
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
        phone = kwargs.get('phone', '').strip()
        reference = kwargs.get('reference', '').strip()

        try:
            if not first_name or not last_name or not phone or not reference:
                raise ValueError("Tous les champs sont obligatoires.")

            patient = request.env['medical.patient'].sudo().search([
                ('first_name', 'ilike', first_name),
                ('last_name', 'ilike', last_name),
                ('phone', '=', phone),
            ], limit=1)

            if not patient:
                raise ValueError("Aucun patient trouvé avec ces informations.")

            rdv = request.env['medical.appointment'].sudo().search([
                ('patient_id', '=', patient.id),
                ('name', '=', reference),
            ], limit=1)

            if not rdv:
                raise ValueError("Aucun rendez-vous trouvé avec cette référence.")

            return request.redirect(f'/medical/espace-patient/{patient.id}')

        except Exception as e:
            return request.render('medical_website.mes_rdv', {
                'searched': True,
                'error': str(e),
            })

    @http.route('/medical/espace-patient/<int:patient_id>', type='http', auth='public', website=True)
    def espace_patient(self, patient_id, **kwargs):
        patient = request.env['medical.patient'].sudo().browse(patient_id)
        if not patient.exists():
            return request.redirect('/medical/mes-rdv')

        rdvs = request.env['medical.appointment'].sudo().search([
            ('patient_id', '=', patient.id),
        ], order='appointment_date desc')

        consultations = request.env['medical.consultation'].sudo().search([
            ('patient_id', '=', patient.id),
            ('state', '=', 'done'),
        ], order='consultation_date desc')

        # Statistiques
        total_rdv = len(rdvs)
        rdv_done = len(rdvs.filtered(lambda r: r.state == 'done'))
        rdv_upcoming = len(rdvs.filtered(lambda r: r.state in ['draft', 'confirmed']))

        return request.render('medical_website.espace_patient', {
            'patient': patient,
            'rdvs': rdvs,
            'consultations': consultations,
            'total_rdv': total_rdv,
            'rdv_done': rdv_done,
            'rdv_upcoming': rdv_upcoming,
        })

    @http.route('/medical', type='http', auth='public', website=True)
    def index(self, **kwargs):
        doctors = request.env['medical.doctor'].sudo().search([], limit=3)
        return request.render('medical_website.index', {
            'doctors': doctors,
        })

    @http.route('/medical/rgpd', type='http', auth='public', website=True)
    def rgpd(self, **kwargs):
        return request.render('medical_website.rgpd', {})