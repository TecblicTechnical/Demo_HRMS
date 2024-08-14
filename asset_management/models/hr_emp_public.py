from odoo import api, models, fields,_

class HrEmployeePublicInherit(models.Model):
    _inherit = 'hr.employee.public'

    equipment_ids = fields.One2many('maintenance.equipment', 'employee_id')
    equipment_count = fields.Integer('Equipments', compute='_compute_equipment_count')
    gmail_pswd = fields.Char("Gmail Password")
    assets_return_date = fields.Datetime("Assets Return Date")
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

    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for employee in self:
            employee.equipment_count = len(employee.equipment_ids)

    def return_allocated_assets(self):
        context = self.env.context.copy()
        context['hide_return_button'] = True
        return {
            "name": _("Return Asset"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "return.asset.details",
            "target": "new",
            "view_id": self.env.ref("asset_management.return_asset_details_form").id,
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