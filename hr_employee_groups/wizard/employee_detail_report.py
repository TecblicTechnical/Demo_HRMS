from odoo import api, fields, models, _
from io import BytesIO
import xlsxwriter

class EmpDetailReport(models.TransientModel):
    _name = 'emp.detail.report'
    _description = 'Employee Detail Report'

    employee_ids = fields.Many2many('hr.employee', string='Employees')

    def print_report_pdf(self):
        return self.env.ref("hr_employee_groups.action_employee_detail_report").report_action(self)

    def print_report_xls(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/employee_detail_sheet_report/%s' % (self.id),
            'target': 'new',
        }

    def generate_emp_detail_report(self, id):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Sheet 1')
        record = self.env['emp.detail.report'].sudo().search([('id', '=', id)])
        row = 2
        colm = 0
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 30)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 30)

        cell_format1 = workbook.add_format({'bold': True, 'font_size': 14,'align':'center','border': 1})
        cell_format2 = workbook.add_format({'font_size':12,'align':'center'})
        cell_format1.set_bg_color('yellow')
        merge_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        merge_format.set_bg_color('#57a0d2')
        merge_format.set_align('vcenter')

        worksheet.merge_range('A2:H2', ' Employee Details ', merge_format)

        if record.employee_ids:
            employee_ids = self.env['hr.employee'].sudo().search([('id', 'in', record.employee_ids.ids)])
        else:
            employee_ids = self.env['hr.employee'].sudo().search([])
        row += 2

        worksheet.write(row, colm, 'Employee Name', cell_format1)
        worksheet.write(row, colm+1, 'Department', cell_format1)
        worksheet.write(row, colm+2, 'Manager', cell_format1)
        worksheet.write(row, colm+3, 'Mobile', cell_format1)
        worksheet.write(row, colm+4, 'Email', cell_format1)
        worksheet.write(row, colm+5, 'Completion Date', cell_format1)
        worksheet.write(row, colm+6, 'Joining Date', cell_format1)
        worksheet.write(row, colm+7, 'Total Experience', cell_format1)
        row += 1
        for emp in employee_ids:
            worksheet.write(row, colm, f"{emp.name}",cell_format2)
            worksheet.write(row, colm+1, f"{emp.department_id.name or ''}", cell_format2)
            worksheet.write(row, colm+2, f"{emp.parent_id.name or ''}", cell_format2)
            worksheet.write(row, colm+3, f"{emp.mobile_phone or ''}", cell_format2)
            worksheet.write(row, colm+4, f"{emp.work_email or ''}", cell_format2)
            worksheet.write(row, colm+5, f"{emp.completion_date.strftime('%d-%m-%Y') if emp.completion_date else ''}", cell_format2)
            worksheet.write(row, colm+6, f"{emp.joining_date.strftime('%d-%m-%Y') if emp.joining_date else ''}", cell_format2)
            worksheet.write(row, colm+7, f"{emp.total_experience or ''}", cell_format2)
            row += 1
        workbook.close()
        return fp.getvalue()

