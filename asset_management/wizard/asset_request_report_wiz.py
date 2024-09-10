from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from io import BytesIO
import xlsxwriter
import datetime

class AssetRequestReport(models.TransientModel):
    _name = 'asset.request.report'
    _description = 'Asset Request Report'

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)

    @api.constrains('date_to')
    def _check_date_constraint(self):
        if self.date_to < self.date_from:
            raise ValidationError(_("To date should be greater than From date."))

    def print_asset_request_report_pdf(self):
        return self.env.ref("asset_management.action_employee_asset_request_pdf_reports").report_action(self)

    def print_asset_request_report_xls(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/employee_asset_request_xlsx_report/%s' % (self.id),
            'target': 'new',
        }

    def generate_emp_asset_request_report(self, id):
        record = self.env['asset.request.report'].sudo().search([('id', '=', id)])
        date_from_str = str(record.date_from)
        date_to_str = str(record.date_to)

        date_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d').date()
        date_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d').date()



        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Sheet 1')
        row = 1
        colm = 0

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 35)
        worksheet.set_column('D:D', 25)

        cell_format_normal = workbook.add_format({'font_size': 12, 'align': 'center'})
        cell_format_emp_details = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        merge_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        merge_format.set_bg_color('#57a0d2')
        merge_format.set_align('vcenter')
        cell_format_emp_details.set_bg_color('#b9bbb6')

        worksheet.merge_range('A1:D1', "Employee Asset Request Sheet", merge_format)
        row += 1

        if record.employee_ids and (date_from and date_to):
            asset_ids = self.env['asset.request'].sudo().search(
                [('employee_id', 'in', record.employee_ids.ids), ('create_date', '>=', date_from),
                 ('create_date', '<=', date_to)])
        else:
            asset_ids = self.env['asset.request'].sudo().search(
                [('create_date', '>=', date_from), ('create_date', '<=', date_to)])

        row += 1
        colm = 0
        worksheet.write(row, colm, 'Request Date', cell_format_emp_details)
        worksheet.write(row, colm + 1, 'Employee Name', cell_format_emp_details)
        worksheet.write(row, colm + 2, 'Asset Request', cell_format_emp_details)
        worksheet.write(row, colm + 3, 'Status', cell_format_emp_details)
        row += 1
        colm = 0
        for ast in asset_ids:
            formatted_date = ast.create_date.strftime('%Y-%m-%d')
            state_string = ast._fields['state'].convert_to_export(ast.state, ast)

            worksheet.set_row(row, 40)
            worksheet.write(row, colm, formatted_date or '', cell_format_normal)
            worksheet.write(row, colm + 1, ast.employee_id.name or '', cell_format_normal)
            worksheet.write(row, colm + 2, ast.name or '', cell_format_normal)
            worksheet.write(row, colm + 3, state_string or '', cell_format_normal)
            row = row + 1
        row = row + 2
        workbook.close()
        return fp.getvalue()
