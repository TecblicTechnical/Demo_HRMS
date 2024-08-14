from odoo import models, api, fields,_
from odoo.exceptions import ValidationError

class CustomMaintenance(models.Model):
    _inherit = 'maintenance.request'

    asset_seq = fields.Char(related='equipment_id.sequence', string='Asset Sequence')
    asset_assign_date = fields.Date(related='equipment_id.assign_date', string='Asset Assign Date')
    asset_assign_to = fields.Many2one(related='equipment_id.employee_id', string='Asset Assign To')
    hide_manager_approve_btn = fields.Boolean('Hide for User',compute="compute_manager_approve_button_hide")
    active = fields.Boolean(string='Active', index=True, default=True)

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('manager_approval', 'Manager Approval'),
        ('validate', 'Approved')
    ], string='Status',default='draft', tracking=True)

    def compute_manager_approve_button_hide(self):
        for rec in self:
            rec.hide_manager_approve_btn = False
            if rec.env.user.employee_id.id == rec.employee_id.id and not self.env.user.has_group("asset_management.asset_admin_group"):
                rec.hide_manager_approve_btn = True

    def action_approve(self):
        is_admin = self.env.user.has_group('asset_management.asset_admin_group')
        if is_admin:
            for rec in self:
                template = self.env.ref('asset_management.send_assets_maintenance_request_asset_manager_mail',
                                        raise_if_not_found=False)
                email_values = {
                    'email_from': self.env.user.employee_id.work_email,
                    'email_to': rec.employee_id.work_email,
                }
                template.send_mail(rec.id, force_send=True, email_values=email_values)
                rec.state = 'validate'
                if rec.equipment_id.equipment_assign_to == 'department':
                    rec.equipment_id.department_id = False

                if rec.equipment_id.equipment_assign_to == 'employee':
                    rec.equipment_id.employee_id = False
        else:
            raise ValidationError(_("Only Admin Can Approve Request...!"))

    def action_confirm(self):
        self = self.sudo()
        for record in self:
            template = self.env.ref('asset_management.send_maintenance_request_mail', raise_if_not_found=False)


            users_in_group = self.env['res.users'].search([('groups_id.name', '=', 'Assets Manager')])
            asset_manager_emails = users_in_group.mapped('work_email')
            if record.employee_id.parent_id:
                email_to = record.employee_id.parent_id.work_email
            else:
                email_to = asset_manager_emails
            email_values = {
                'email_from': record.employee_id.work_email,
                'email_to': email_to,
            }
            template.send_mail(record.id, force_send=True, email_values=email_values)
            self.write({'state': 'confirm'})
        return True

    def action_manager_approval(self):
        is_manager = self.env.user.has_group('asset_management.assets_manager_group')
        is_admin = self.env.user.has_group('asset_management.asset_admin_group')

        if is_admin or is_manager:
            for rec in self:
                users_in_group = self.env['res.users'].search([('groups_id.name', '=', 'Assets Administrator')])
                employees_in_group = users_in_group.mapped('employee_ids')
                asset_manager_emails = employees_in_group.mapped('work_email')

                if asset_manager_emails:
                    email_cc = ','.join(asset_manager_emails)
                else:
                    email_cc = ''

                template = self.env.ref('asset_management.assets_maintenance_request_manager_approval_mail',
                                        raise_if_not_found=False)
                email_values = {
                    'email_from': self.env.user.employee_id.work_email,
                    'email_to': rec.employee_id.work_email,
                    'email_cc': email_cc,
                }
                template.send_mail(rec.id, force_send=True, email_values=email_values)
                rec.state = 'manager_approval'
        else:
            raise ValidationError(_("Only Manager OR Admin Can Approve Request...!"))

    def action_refuse(self):
        for record in self:
            users_in_group = self.env['res.users'].search([('groups_id.name', '=', 'Assets Administrator')])
            employees_in_group = users_in_group.mapped('employee_ids')
            asset_manager_emails = employees_in_group.mapped('work_email')

            if asset_manager_emails:
                email_cc = ','.join(asset_manager_emails)
            else:
                email_cc = ''

            template = self.env.ref('asset_management.send_maintenance_request_refuse_mail', raise_if_not_found=False)
            email_values = {
                'email_from': self.env.user.employee_id.work_email,
                'email_to': record.employee_id.work_email,
                'email_cc': email_cc,
            }
            template.send_mail(record.id, force_send=True, email_values=email_values)
            self.write({'state': 'refuse'})
        return True

    def action_draft(self):
        self.state = 'draft'
