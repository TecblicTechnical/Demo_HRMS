from odoo import api, models, _
import datetime

class EmpLeaveReport(models.AbstractModel):
    _name = 'report.time_off_approval_flow.report_employee_leave_template'
    _description = 'Employee Leave Report Template'

    def _get_report_values(self, docids, data=None):
        record = self.env['employee.leave.request.report'].browse(docids)
        date_from_str = str(record.date_from)
        date_to_str = str(record.date_to)

        date_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d').date()
        date_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d').date()

        if record.employee_ids and (date_from and date_to):
            employee_ids = self.env['hr.leave'].sudo().search([('employee_ids','in', record.employee_ids.ids),('request_date_from', '>=', date_from),('request_date_to', '<=', date_to)])
        else:
            employee_ids = self.env['hr.leave'].sudo().search([('request_date_from', '>=', date_from),('request_date_to', '<=', date_to)])

        data.update({
            'date_range': str(date_from) + ' to ' + str(date_to),
            'emp_leave_req_list': employee_ids
        })
        return {
            'data': data
        }
