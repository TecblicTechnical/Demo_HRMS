from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError, ValidationError


class ReturnAssetDetails(models.TransientModel):
    _name = 'return.asset.details'
    _description = 'Return Asset Details'

    gmail_pswd = fields.Char("Gmail Password")
    assets_return_date = fields.Datetime("Assets Return Date",default=lambda self: fields.Datetime.now())
    equipment_ids = fields.Many2many('maintenance.equipment',  string='Equipment')

    @api.model
    def default_get(self, fields):
        res = super(ReturnAssetDetails, self).default_get(fields)
        records = self.env['hr.employee.public'].browse(self.env.context.get('active_ids'))
        for rec in records:
            res.update({
                'gmail_pswd': rec.gmail_pswd if rec.gmail_pswd else '',
                'equipment_ids': [(6, 0, rec.equipment_ids.ids)]
            })
        return res


    def action_return_asset_details(self):
        active_id = self.env.context.get('active_id')
        if not active_id:
            raise UserError(_('Active ID not found!'))

        employee = self.env['hr.employee.public'].sudo().search([('id', '=', active_id)])
        if not employee:
            raise UserError(_('Employee not found!'))

        employee.sudo().write({
            'gmail_pswd': self.gmail_pswd if self.gmail_pswd else '',
            'assets_return_date': self.assets_return_date,
        })
        template = self.env.ref('asset_management.send_return_assets_mail', raise_if_not_found=False)
        equipment_ids = employee.equipment_ids.filtered(lambda x: not x.is_mail_send)
        equipment_ids.write({'is_mail_send': True})
        if template:
            self = self.sudo()
            users_in_group = self.env['res.users'].search([('groups_id.name', '=', 'Assets Administrator')])
            employees_in_group = users_in_group.mapped('employee_ids')
            asset_manager_emails = employees_in_group.mapped('work_email')
            email_values = {
                'email_from': employee.work_email,
                'email_to': asset_manager_emails,
                'email_cc': employee.parent_id.work_email,
            }
            template.send_mail(employee.id, force_send=True, email_values=email_values)
        else:
            print("\n \n \nTemplate 'send_return_assets_mail' not found. \n \n \n")
        equipment_ids.write({'employee_id': False})
