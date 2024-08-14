from odoo import api, models, fields,_

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    gmail_pswd = fields.Char("Gmail Password")
    assets_return_date = fields.Datetime("Assets REturn Date")
    all_equipment_received = fields.Boolean(
        string='All Equipment Received',
        compute='_compute_all_equipment_received',
    )
    hide_return_button = fields.Boolean('Hide return button', compute='_compute_hide_return_button')


    @api.depends('equipment_ids.is_mail_send')
    def _compute_hide_return_button(self):
        for employee in self:
            hide_button = all(equipment.is_mail_send for equipment in employee.equipment_ids)
            employee.hide_return_button = hide_button

    @api.depends('equipment_ids.state')
    def _compute_all_equipment_received(self):
        for employee in self:
            all_received = all(equipment.state == 'received_by_emp' for equipment in employee.equipment_ids)
            employee.all_equipment_received = all_received

    def allocate_assets_to_employee(self):
        for employee in self:
            template = self.env.ref('asset_management.send_assets_allocated_mail', raise_if_not_found=False)
            if template:
                users_in_group = self.env['res.users'].search([('groups_id.name', '=', 'Assets Administrator')])
                employees_in_group = users_in_group.mapped('employee_ids')
                asset_manager_emails = employees_in_group.mapped('work_email')
                email_values = {
                    'email_from': asset_manager_emails,
                    'email_to': employee.work_email,
                    'email_cc': employee.parent_id.work_email,
                }
                template.send_mail(employee.id, force_send=True, email_values=email_values)
                self.message_post_with_template(template.id)
            else:
                print("\n \n \nTemplate 'send_assets_allocated_mail' not found. \n \n \n")


    def return_allocated_assets(self):
        return {
            "name": _("Return Asset"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "return.asset.details",
            "target": "new",
            "view_id": self.env.ref("asset_management.return_asset_details_form").id,
            "context": {'hide_return_button': True},
        }

    def employee_receive_asset_approval(self):
        return {
            "name": _("Received Asset Approval"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "employee.received.assets.wizard",
            "target": "new",
            "view_id": self.env.ref("asset_management.view_emp_received_approval_wizard_form_id").id,
        }