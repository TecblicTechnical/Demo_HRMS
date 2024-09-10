from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from io import BytesIO
import xlsxwriter
import datetime


class EmployeeLeaveRequestReport(models.TransientModel):
    _name = 'employee.leave.request.report'
    _description = 'Employee Leave Request Report'

    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees')

    @api.constrains('date_to')
    def _check_date_constraint(self):
        if self.date_to < self.date_from:
            raise ValidationError(_("To date should be greater than From date."))

    def print_leave_request_report_pdf(self):
        return self.env.ref("time_off_approval_flow.action_employee_leave_request_pdf_reports").report_action(self)

    def print_leave_request_report_xls(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/employee_leave_request_xlsx_report/%s' % (self.id),
            'target': 'new',
        }

    def generate_emp_leave_request_report(self, id):
        record = self.env['employee.leave.request.report'].sudo().search([('id', '=', id)])

        print("record.date_from..........", record.date_from)
        print("record.date_to..........", record.date_to)

        date_from_str = str(record.date_from)
        date_to_str = str(record.date_to)

        print("date_from_str..........", date_from_str)
        print("date_to_str..........", date_to_str)

        date_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d').date()
        date_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d').date()

        print("date_from.date_from..........", date_from)
        print("date_to.date_to..........", date_to)

        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Sheet 1')
        row = 1
        colm = 0

        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 35)
        worksheet.set_column('F:F', 25)


        cell_format_normal = workbook.add_format({'font_size': 12, 'align': 'center'})
        cell_format_emp_details = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        merge_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        merge_format.set_bg_color('#57a0d2')
        merge_format.set_align('vcenter')
        cell_format_emp_details.set_bg_color('#b9bbb6')

        worksheet.merge_range('B1:E1', "Employee Leave Request Sheet", merge_format)
        row += 1

        if record.employee_ids and (date_from and date_to):
            leave_ids = self.env['hr.leave'].sudo().search([('employee_ids', 'in', record.employee_ids.ids), ('request_date_from', '>=', date_from), ('request_date_to', '<=', date_to)])
        else:
            leave_ids = self.env['hr.leave'].sudo().search([('request_date_from', '>=', date_from), ('request_date_to', '<=', date_to)])

        row += 1
        colm = 0
        worksheet.write(row, colm, 'Employee Name', cell_format_emp_details)
        worksheet.write(row, colm + 1, 'Start Date', cell_format_emp_details)
        worksheet.write(row, colm + 2, 'End Date', cell_format_emp_details)
        worksheet.write(row, colm + 3, 'Description', cell_format_emp_details)
        worksheet.write(row, colm + 4, 'Status', cell_format_emp_details)
        row += 1
        colm = 0
        for rec in leave_ids:
            formatted_date1 = rec.request_date_from.strftime('%Y-%m-%d')
            formatted_date2 = rec.request_date_to.strftime('%Y-%m-%d')
            state_string = rec._fields['state'].convert_to_export(rec.state, rec)
            worksheet.set_row(row, 40)
            worksheet.write(row, colm, rec.employee_ids.name or '', cell_format_normal)
            worksheet.write(row, colm + 1, formatted_date1 or '', cell_format_normal)
            worksheet.write(row, colm + 2, formatted_date2 or '', cell_format_normal)
            worksheet.write(row, colm + 3, rec.name or '', cell_format_normal)
            worksheet.write(row, colm + 4, state_string or '', cell_format_normal)
            row = row + 1
        row = row + 2
        workbook.close()
        return fp.getvalue()
