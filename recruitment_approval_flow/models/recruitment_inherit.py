from odoo import api, models, fields,_
from odoo.exceptions import ValidationError


class Job(models.Model):
    _inherit = "hr.job"

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate', 'Approved')
    ], string='Status', default='draft', tracking=True)
    hide_approve_btn = fields.Boolean('Can Approve',compute='compute_hide_manager_approve_button')
    description = fields.Char(string='Job Description')


    def compute_hide_manager_approve_button(self):
        for rec in self:
            rec.hide_approve_btn = False
            if rec.env.user.employee_id.id == rec.create_uid.employee_id.id and not self.env.user.has_group("hr_recruitment.group_hr_recruitment_manager"):
                rec.hide_approve_btn = True

    def action_approve(self):
        is_admin = self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager')
        if is_admin:
            for record in self:
                template = self.env.ref('recruitment_approval_flow.job_position_approved_mail',
                                        raise_if_not_found=False)
                group = self.env.ref('hr_recruitment.group_hr_recruitment_manager')
                emails = group.users.mapped('email')
                if emails:
                    email_from = emails
                else:
                    email_from = ''
                email_values = {
                    'email_from': email_from,
                    'email_to': record.create_uid.employee_id.work_email,
                }
                template.send_mail(record.id, force_send=True, email_values=email_values)
                record.state = 'validate'
        else:
            raise ValidationError(_("Only Admin Can Approve Request...!"))

    def action_confirms(self):
        self = self.sudo()
        for record in self:
            template = self.env.ref('recruitment_approval_flow.send_job_position_opening_request_mail', raise_if_not_found=False)
            group = self.env.ref('hr_recruitment.group_hr_recruitment_manager')
            emails = group.users.mapped('email')
            if emails:
                email_to = emails
            else:
                email_to = ''

            email_values = {
                'email_from': record.create_uid.employee_id.work_email,
                'email_to': email_to,
            }
            template.send_mail(record.id, force_send=True, email_values=email_values)
            self.write({'state': 'confirm'})
        return True


    def action_refuse(self):
        for record in self:
            template = self.env.ref('recruitment_approval_flow.job_position_refused_mail', raise_if_not_found=False)
            self = self.sudo()
            email_values = {
                'email_from': self.env.user.employee_id.work_email,
                'email_to': record.create_uid.employee_id.work_email ,
            }
            template.send_mail(record.id, force_send=True, email_values=email_values)
            self.write({'state': 'refuse'})
        return True

    def action_draft(self):
        self.state = 'draft'
