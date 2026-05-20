/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { user } from "@web/core/user";

export class MedicalDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.session = session;
        
        this.state = useState({
            appointments: [],
            is_doctor: false,
            has_access: true,
        });

        onWillStart(async () => {
            const isDoctor = await user.hasGroup("medical_base.group_medical_doctor");
            const isSecretary = await user.hasGroup("medical_base.group_medical_secretary");
            const isAdmin = await user.hasGroup("base.group_erp_manager");
            
            this.state.has_access = isDoctor || isSecretary || isAdmin;
            
            if (!this.state.has_access) {
                return;
            }

            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            const tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);
            
            // Format for Odoo ORM (UTC)
            // Note: Simplification for prototype: using local date strings directly formatted
            // Odoo usually expects UTC string for datetime fields.
            const formatToUTCString = (date) => {
                return date.toISOString().split('.')[0].replace('T', ' ');
            };
            
            const todayStr = formatToUTCString(today);
            const tomorrowStr = formatToUTCString(tomorrow);

            // Try to find a doctor matching the user's name
            const doctors = await this.orm.searchRead(
                "medical.doctor", 
                [["name", "ilike", session.name]], 
                ["id"]
            );
            
            let domain = [
                ["appointment_date", ">=", todayStr],
                ["appointment_date", "<", tomorrowStr],
                ["state", "!=", "cancelled"]
            ];
            
            if (doctors.length > 0) {
                domain.push(["doctor_id", "=", doctors[0].id]);
                this.state.is_doctor = true;
            } else {
                this.state.is_doctor = false;
            }

            const appointments = await this.orm.searchRead(
                "medical.appointment",
                domain,
                ["name", "patient_id", "doctor_id", "appointment_date", "state"]
            );

            appointments.forEach(app => {
                if (app.appointment_date) {
                    const timePart = app.appointment_date.split(' ')[1];
                    if (timePart) {
                        app.time_display = timePart.substring(0, 5);
                    } else {
                        app.time_display = "--:--";
                    }
                }
            });

            appointments.sort((a, b) => {
                if (a.appointment_date < b.appointment_date) return -1;
                if (a.appointment_date > b.appointment_date) return 1;
                return 0;
            });

            this.state.appointments = appointments;
        });
    }

    async openConsultation(appointmentId) {
        const consultations = await this.orm.searchRead(
            "medical.consultation",
            [["appointment_id", "=", appointmentId]],
            ["id"]
        );

        if (consultations.length > 0) {
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "medical.consultation",
                res_id: consultations[0].id,
                views: [[false, "form"]],
                target: "current",
            });
        } else {
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "medical.consultation",
                views: [[false, "form"]],
                target: "current",
                context: {
                    default_appointment_id: appointmentId,
                }
            });
        }
    }
}
MedicalDashboard.template = "medical_appointment.Dashboard";

registry.category("actions").add("medical_dashboard_action", MedicalDashboard);
