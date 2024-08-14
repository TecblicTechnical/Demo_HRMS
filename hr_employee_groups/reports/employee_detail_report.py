from odoo import api, models, _
from dateutil.relativedelta import relativedelta
import datetime


class ReportEmployeeDetailReport(models.AbstractModel):
    _name = 'report.hr_employee_groups.report_employee_detail_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        record = self.env['emp.detail.report'].browse(docids)

        if record.employee_ids:
            employee_ids = self.env['hr.employee'].sudo().search([('id', 'in', record.employee_ids.ids)])
        else:
            employee_ids = self.env['hr.employee'].sudo().search([])

        data.update({
            'employees_details': employee_ids
        })
        return {
            'data': data
        }
