from odoo import models, fields, api


class EmployeeReceivedAssetWizard(models.TransientModel):
    _name = 'employee.received.assets.wizard'
    _description = 'Employee Received Assets Wizard'

    remark = fields.Char(string='Remark')
    equipment_ids = fields.Many2many('maintenance.equipment', string='Equipment')
    # signature = fields.Binary(string='Signature')

    # @api.model
    # def default_get(self, fields):
    #     res = super(EmployeeReceivedAssetWizard, self).default_get(fields)
    #     records = self.env['hr.employee'].browse(self.env.context.get('active_ids'))
    #     for rec in records:
    #         res.update({
    #             'equipment_ids': [(6, 0, rec.equipment_ids.ids)]
    #         })
    #     return res

    @api.model
    def default_get(self, fields):
        res = super(EmployeeReceivedAssetWizard, self).default_get(fields)
        records = self.env['hr.employee'].browse(self.env.context.get('active_ids'))
        equipment_ids = []
        for rec in records:
            filtered_equipment_ids = rec.equipment_ids.filtered(lambda x: x.state != 'received_by_emp')
            equipment_ids += filtered_equipment_ids.ids
        res.update({
            'equipment_ids': [(6, 0, equipment_ids)]
        })
        return res

    def received_assets_approval(self):
        for equipment in self:
            for rec in equipment.equipment_ids:
                if rec.remove_selected_data:
                    rec.write({
                        'state': 'received_by_emp',
                        'emp_remark': equipment.remark
                    })
                else:
                    rec.write({
                        'state': 'allocated',
                        'emp_remark': False
                    })
                equipment.refresh()

