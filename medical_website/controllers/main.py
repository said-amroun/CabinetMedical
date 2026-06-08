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
        from datetime import datetime, timedelta
        doctors = request.env['medical.doctor'].sudo().search([])

        day_labels = ['Lun.', 'Mar.', 'Mer.', 'Jeu.', 'Ven.', 'Sam.', 'Dim.']
        slot_pool = ['09:00', '10:30', '11:30', '14:00', '14:30', '15:30', '16:30']

        next_days = []
        now = datetime.now()
        cursor = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Boucle jusqu'à avoir 3 jours avec créneaux dispo (max 14 jours d'essai)
        for _ in range(14):
            if len(next_days) >= 3:
                break
            if cursor.weekday() < 6:  # Lundi=0 ... Samedi=5 (exclut dimanche=6)
                available = []
                for s in slot_pool:
                    h, m = int(s[:2]), int(s[3:5])
                    slot_dt = cursor.replace(hour=h, minute=m)
                    if slot_dt > now:
                        available.append(s)
                if available:
                    next_days.append({
                        'label': day_labels[cursor.weekday()],
                        'num': cursor.strftime('%d'),
                        'slots': available[:3],
                    })
            cursor += timedelta(days=1)

        return request.render('medical_website.medecins', {
            'doctors': doctors,
            'next_days': next_days,
        })

    @http.route('/medical/rdv', type='http', auth='public', website=True)
    def rdv(self, doctor_id=None, **kwargs):
        from datetime import datetime, timedelta

        # Si pas de médecin sélectionné, rediriger vers la liste
        if not doctor_id:
            return request.redirect('/medical/medecins')

        selected_doctor = request.env['medical.doctor'].sudo().browse(int(doctor_id))
        doctors = request.env['medical.doctor'].sudo().search([])

        today = datetime.now().strftime('%Y-%m-%d')
        max_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')

        return request.render('medical_website.rdv', {
            'doctors': doctors,
            'selected_doctor': selected_doctor,
            'today': today,
            'max_date': max_date,
        })

    @http.route('/medical/rdv/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def submit_rdv(self, **kwargs):
        from datetime import datetime, timedelta
        import pytz
        doctors = request.env['medical.doctor'].sudo().search([])
        try:
            doctor_id = int(kwargs.get('doctor_id', 0))
            appointment_date = kwargs.get('appointment_date')
            first_name = kwargs.get('first_name', '').strip()
            last_name = kwargs.get('last_name', '').strip()
            phone = kwargs.get('phone', '').strip()
            email = kwargs.get('email', '').strip()
            birth_date = kwargs.get('birth_date', '').strip()
            gender = kwargs.get('gender', '').strip()

            if not doctor_id or not appointment_date or not first_name or not last_name:
                raise ValueError("Tous les champs obligatoires doivent être remplis.")

            # Validation date de naissance (doit être dans le passé)
            if not birth_date:
                raise ValueError("La date de naissance est obligatoire.")
            try:
                birth_dt = datetime.strptime(birth_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Format de date de naissance invalide.")
            if birth_dt >= datetime.now().date():
                raise ValueError("La date de naissance doit être antérieure à aujourd'hui.")

            # Validation genre
            if gender not in ('male', 'female'):
                raise ValueError("Veuillez sélectionner un genre.")

            # Heure LOCALE choisie par l'utilisateur
            date_local = datetime.strptime(appointment_date, '%Y-%m-%dT%H:%M')

            # Validations sur l'heure LOCALE (avant conversion UTC)
            if not (8 <= date_local.hour < 17):
                raise ValueError("Les RDV sont disponibles uniquement entre 08h00 et 17h00.")

            if date_local.weekday() >= 5:
                raise ValueError("Les RDV ne sont pas disponibles le weekend.")

            # Conversion en UTC pour stockage
            user_tz = pytz.timezone('Europe/Paris')
            date_utc = user_tz.localize(date_local).astimezone(pytz.utc).replace(tzinfo=None)

            if date_utc < datetime.utcnow():
                raise ValueError("La date choisie est déjà passée.")

            # Recherche / création du patient
            patient = request.env['medical.patient'].sudo().search([
                ('first_name', 'ilike', first_name),
                ('last_name', 'ilike', last_name),
                ('phone', '=', phone),
            ], limit=1)

            patient_vals = {
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'email': email,
                'birth_date': birth_dt,
                'gender': gender,
            }

            if not patient:
                patient = request.env['medical.patient'].sudo().create(patient_vals)
            else:
                # Mise à jour des infos si patient existant
                patient.sudo().write(patient_vals)

            # ===== CONTRAINTE 1 : un seul RDV par jour avec le même médecin =====
            start_of_day = date_local.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date_local.replace(hour=23, minute=59, second=59, microsecond=0)
            start_utc = user_tz.localize(start_of_day).astimezone(pytz.utc).replace(tzinfo=None)
            end_utc = user_tz.localize(end_of_day).astimezone(pytz.utc).replace(tzinfo=None)

            existing_same_doctor = request.env['medical.appointment'].sudo().search([
                ('patient_id', '=', patient.id),
                ('doctor_id', '=', doctor_id),
                ('appointment_date', '>=', start_utc),
                ('appointment_date', '<=', end_utc),
                ('state', '!=', 'cancelled'),
            ], limit=1)
            if existing_same_doctor:
                raise ValueError("Vous avez déjà un rendez-vous avec ce médecin ce jour-là.")

            # ===== CONTRAINTE 2 : pas de RDV au même créneau avec un autre médecin =====
            existing_same_slot = request.env['medical.appointment'].sudo().search([
                ('patient_id', '=', patient.id),
                ('appointment_date', '=', date_utc),
                ('state', '!=', 'cancelled'),
            ], limit=1)
            if existing_same_slot:
                raise ValueError("Vous avez déjà un rendez-vous à cette heure avec un autre médecin.")

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
            doctor_id_raw = kwargs.get('doctor_id')
            if doctor_id_raw:
                selected_doctor = request.env['medical.doctor'].sudo().browse(int(doctor_id_raw))

            # Nettoyer le message d'erreur
            error_msg = str(e)
            if 'ValidationError' in error_msg:
                error_msg = error_msg.split('\n')[-1]

            today_str = datetime.now().strftime('%Y-%m-%d')
            max_date_str = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')

            return request.render('medical_website.rdv', {
                'doctors': doctors,
                'selected_doctor': selected_doctor,
                'today': today_str,
                'max_date': max_date_str,
                'error': error_msg,
                'form_data': {
                    'first_name': kwargs.get('first_name', ''),
                    'last_name': kwargs.get('last_name', ''),
                    'phone': kwargs.get('phone', ''),
                    'email': kwargs.get('email', ''),
                    'birth_date': kwargs.get('birth_date', ''),
                    'gender': kwargs.get('gender', ''),
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
        email = kwargs.get('email', '').strip()
        birth_date = kwargs.get('birth_date', '').strip()

        if not first_name or not last_name or not email or not birth_date:
            return request.render('medical_website.mes_rdv', {
                'error': "Tous les champs sont obligatoires.",
                'searched': False,
            })

        patient = request.env['medical.patient'].sudo().search([
            ('first_name', 'ilike', first_name),
            ('last_name', 'ilike', last_name),
            ('email', '=ilike', email),
            ('birth_date', '=', birth_date),
        ], limit=1)

        if not patient:
            return request.render('medical_website.mes_rdv', {
                'error': "Aucun patient trouvé avec ces informations.",
                'searched': True,
                'rdvs': False,
            })

        rdvs = request.env['medical.appointment'].sudo().search([
            ('patient_id', '=', patient.id),
        ], order='appointment_date desc')

        consultations = request.env['medical.consultation'].sudo().search([
            ('patient_id', '=', patient.id),
        ], order='consultation_date desc')

        return request.render('medical_website.mes_rdv', {
            'searched': True,
            'patient': patient,
            'rdvs': rdvs,
            'consultations': consultations,
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

    @http.route('/medical/rdv/cancel', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def cancel_rdv(self, **kwargs):
        rdv_id = kwargs.get('rdv_id')
        patient_id = kwargs.get('patient_id')
        if not rdv_id or not patient_id:
            return request.redirect('/medical/mes-rdv')
        try:
            rdv = request.env['medical.appointment'].sudo().browse(int(rdv_id))
            # Sécurité : on vérifie que le RDV appartient bien au patient
            if rdv and rdv.patient_id.id == int(patient_id) and rdv.state in ('draft', 'confirmed'):
                rdv.sudo().write({'state': 'cancelled'})
        except Exception:
            request.env.cr.rollback()
        return request.redirect('/medical/espace-patient/' + str(patient_id))

    @http.route('/medical/rdv/details/<int:rdv_id>', type='http', auth='public', website=True)
    def rdv_details(self, rdv_id, **kwargs):
        rdv = request.env['medical.appointment'].sudo().browse(rdv_id)
        if not rdv.exists():
            return request.redirect('/medical/mes-rdv')
        return request.render('medical_website.rdv_details', {
            'rdv': rdv,
        })