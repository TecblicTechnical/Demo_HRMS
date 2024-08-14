from odoo import api, models, _

class ReportEquipmentAssetReporTmplReport(models.AbstractModel):
    _name = 'report.asset_management.equipment_asset_report_tmpl'
    _description = 'Equipment Asset Request Template'

    def _get_report_values(self, docids, data=None):
        record = self.env['equipment.asset.report'].browse(docids)
        if record.employee_ids or record.department_ids:
            employee_ids = self.env['maintenance.equipment'].sudo().search(['|',('employee_id','in', record.employee_ids.ids),('department_id', 'in', record.department_ids.ids)])
        else:
            employee_ids = self.env['maintenance.equipment'].sudo().search([])

        data.update({
            'employee_asset_list': employee_ids
        })
        return {
            'data': data
        }
