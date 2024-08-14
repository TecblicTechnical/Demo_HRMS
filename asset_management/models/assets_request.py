from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

class AssetRequest(models.Model):
    _name = 'asset.request'
    _description = 'Asset Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_employee(self):
        return self.env.user.employee_id

    name = fields.Char("Asset Request")
    assets_manager_remark = fields.Char("Remark")
    employee_id = fields.Many2one("hr.employee", string="Employee",  default=_default_employee, required=True,
                                  ondelete='cascade', index=True, store=True)
    is_asset_manager = fields.Boolean("Is Assets Manager")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('manager_approval', 'Manager Approval'),
        ('validate', 'Approved')
    ], string='Status',default='draft', tracking=True)
    hide_manager_approve_btn = fields.Boolean('Can Approve',compute='compute_manager_approve_button_hide')
    active = fields.Boolean(string='Active', index=True, default=True)


    def action_approve(self):
        is_admin = self.env.user.has_group('asset_management.asset_admin_group')
        if is_admin:
            for rec in self:
                template = self.env.ref('asset_management.send_assets_request_asset_manager_mail', raise_if_not_found=False)
                email_values = {
                    'email_from': self.env.user.employee_id.work_email,
                    'email_to': rec.employee_id.work_email,
                }
                template.send_mail(rec.id, force_send=True, email_values=email_values)
                rec.state = 'validate'
        else:
            raise ValidationError(_("Only Admin Can Approve Request...!"))

    def action_confirm(self):
        self = self.sudo()
        for record in self:
            template = self.env.ref('asset_management.send_assets_request_mail', raise_if_not_found=False)
            if record.employee_id.parent_id:
                email_to = record.employee_id.parent_id.work_email
            else:
                email_to = ''

            users_in_group = self.env['res.users'].search([('groups_id.name', '=', 'Assets Administrator')])
            asset_manager_emails = users_in_group.mapped('work_email')

            if asset_manager_emails:
                email_cc = ','.join(asset_manager_emails)
            else:
                email_cc = ''

            email_values = {
                'email_from': record.employee_id.work_email,
                'email_to': email_to,
                'email_cc': email_cc,
            }
            template.send_mail(record.id, force_send=True,email_values=email_values)
            self.write({'state': 'confirm'})
        return True

    def action_manager_approval(self):
        is_manager = self.env.user.has_group('asset_management.assets_manager_group')
        is_admin = self.env.user.has_group('asset_management.asset_admin_group')

        if is_admin or is_manager :
            for rec in self:
                # users_in_group = self.env['res.users'].search([('groups_id.name', '=', 'Assets Administrator')])
                # employees_in_group = users_in_group.mapped('employee_ids')
                # asset_manager_emails = employees_in_group.mapped('work_email')
                # asset_manager_emails.append('hr@tecblic.com')
                #
                # if asset_manager_emails:
                #     email_cc = ','.join(asset_manager_emails)
                # else:
                #     email_cc = ''
                #
                # template = self.env.ref('asset_management.assets_request_manager_approval_mail', raise_if_not_found=False)
                # email_values = {
                #     'email_from': self.env.user.employee_id.work_email,
                #     'email_to': rec.employee_id.work_email,
                #     'email_cc': email_cc,
                # }
                # template.send_mail(rec.id, force_send=True, email_values=email_values)
                rec.state = 'manager_approval'
        else:
            raise ValidationError(_("Only Manager OR Admin Can Approve Request...!"))


    def action_refuse(self):
        for record in self:
            self = self.sudo()
            users_in_group = self.env['res.users'].search([('groups_id.name', '=', 'Assets Administrator')])
            employees_in_group = users_in_group.mapped('employee_ids')
            asset_manager_emails = employees_in_group.mapped('work_email')

            if asset_manager_emails:
                email_cc = ','.join(asset_manager_emails)
            else:
                email_cc = ''

            template = self.env.ref('asset_management.send_assets_request_refuse_mail', raise_if_not_found=False)
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


    def compute_manager_approve_button_hide(self):
        for rec in self:
            rec.hide_manager_approve_btn = False
            if rec.env.user.employee_id.id == rec.employee_id.id and not self.env.user.has_group("asset_management.asset_admin_group"):
                rec.hide_manager_approve_btn = True

