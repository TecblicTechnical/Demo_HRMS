from odoo import api, models, _
from dateutil.relativedelta import relativedelta
import datetime


class ReportEmployeeProbationReport(models.AbstractModel):
    _name = 'report.hr_employee_groups.report_employee_probation_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        record = self.env['emp.probation.report'].browse(docids)
        employee_period_type = dict(record._fields['employee_period_type'].selection).get(record.employee_period_type)
        data.update({
            'employee_period_type': employee_period_type
        })

        employees_details = []
        employee_ids = self.env['hr.employee'].sudo().search([('employee_period_type', '=', record.employee_period_type)])

        for emp in employee_ids:
            delta = relativedelta(emp.completion_date, datetime.date.today())
            remaining_days = ((str(delta.years) + " year, ") if delta.years else '') + ((str(delta.months) + " months,") if delta.months else '') + ((str(delta.days) + " days") if delta.days else '')

            data_dict = {
                'employee_name': emp.name,
                'joining_date': emp.joining_date.strftime('%d-%m-%Y'),
                'completion_date': emp.completion_date.strftime('%d-%m-%Y'),
                'remaining_days': remaining_days
            }
            employees_details.append(data_dict)

        data['employees_details'] = employees_details
        return {
            'data': data
        }
