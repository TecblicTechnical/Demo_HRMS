from odoo import api, fields, models, _

from dateutil.relativedelta import relativedelta
from io import BytesIO
import datetime
import xlsxwriter

class EmpProbationReport(models.TransientModel):
    _name = 'emp.probation.report'
    _description = 'Employee Probation Report'

    employee_period_type = fields.Selection([('trainee','Trainee'),('probation','Probation'),('permanent','Permanent'),('notice','Notice'),('other','Other')],'Employee Period', required=True)

    def print_report_pdf(self):
        return self.env.ref("hr_employee_groups.action_employee_probation_report").report_action(self)

    def print_report_xls(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/employee_probation_sheet_report/%s' % (self.employee_period_type),
            'target': 'new',
        }

    def generate_emp_prob_report(self, employee_period_type):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Sheet 1')
        row = 2
        colm = 0
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 30)

        cell_format1 = workbook.add_format({'bold': True, 'font_size': 14,'align':'center','border': 1})
        cell_format2 = workbook.add_format({'font_size':12,'align':'center'})
        cell_format1.set_bg_color('yellow')
        merge_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        merge_format.set_bg_color('#57a0d2')
        merge_format.set_align('vcenter')

        worksheet.merge_range('A2:D2', employee_period_type.capitalize() + ' Period Details ', merge_format)

        employee_ids = self.env['hr.employee'].sudo().search([('employee_period_type','=', employee_period_type)])
        row += 2

        worksheet.write(row, colm, 'Employee Name', cell_format1)
        worksheet.write(row, colm+1, 'Joining Date', cell_format1)
        worksheet.write(row, colm+2, 'Completion Date', cell_format1)
        worksheet.write(row, colm+3, 'Remaining Days', cell_format1)

        for emp in employee_ids:
            row += 1

            delta = relativedelta(emp.completion_date, datetime.date.today())
            remaining_days_year = ((str(delta.years) + " year, ") if delta.years else '') + ((str(delta.months) + " months,") if delta.months else '') + ((str(delta.days) + " days") if delta.days else '')

            worksheet.write(row, colm, f"{emp.name}" ,cell_format2)
            worksheet.write(row, colm+1, f"{emp.joining_date.strftime('%d-%m-%Y') or ''}" ,cell_format2)
            worksheet.write(row, colm+2, f"{emp.completion_date.strftime('%d-%m-%Y') or ''}" ,cell_format2)
            worksheet.write(row, colm + 3, f"{remaining_days_year}", cell_format2)

        workbook.close()
        return fp.getvalue()
