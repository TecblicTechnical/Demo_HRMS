from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from io import BytesIO
import xlsxwriter
import datetime


class AssetMaintenanceRequestReport(models.TransientModel):
    _name = 'asset.maintenance.request.report'
    _description = 'Asset Maintenance Request Report'

    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees')

    @api.constrains('date_to')
    def _check_date_constraint(self):
        if self.date_to < self.date_from:
            raise ValidationError(_("To date should be greater than From date."))

    def print_asset_maintenance_request_report_pdf(self):
        return self.env.ref("asset_management.action_employee_asset_maintenance_request_pdf_reports").report_action(self)

    def print_maintenance_request_report_xls(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/employee_maintenance_request_xlsx_report/%s' % (self.id),
            'target': 'new',
        }

    def generate_emp_maintenance_request_report(self, id):
        record = self.env['asset.maintenance.request.report'].sudo().search([('id', '=', id)])

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

        worksheet.merge_range('B1:E1', "Employee Asset Request Sheet", merge_format)
        row += 1

        if record.employee_ids and (date_from and date_to):
            asset_ids = self.env['maintenance.request'].sudo().search([('employee_id', 'in', record.employee_ids.ids), ('request_date', '>=', date_from), ('request_date', '<=', date_to)])
        else:
            asset_ids = self.env['maintenance.request'].sudo().search([('request_date', '>=', date_from), ('request_date', '<=', date_to)])

        row += 1
        colm = 0
        worksheet.write(row, colm, 'Request Date', cell_format_emp_details)
        worksheet.write(row, colm + 1, 'Employee Name', cell_format_emp_details)
        worksheet.write(row, colm + 2, 'Asset', cell_format_emp_details)
        worksheet.write(row, colm + 3, 'Asset Sequence', cell_format_emp_details)
        worksheet.write(row, colm + 4, 'Maintenance Request', cell_format_emp_details)
        worksheet.write(row, colm + 5, 'Status', cell_format_emp_details)
        row += 1
        colm = 0
        for ast in asset_ids:
            formatted_date = ast.create_date.strftime('%Y-%m-%d')

            worksheet.set_row(row, 40)
            worksheet.write(row, colm, formatted_date or '', cell_format_normal)
            worksheet.write(row, colm + 1, ast.employee_id.name or '', cell_format_normal)
            worksheet.write(row, colm + 2, ast.equipment_id.name or '', cell_format_normal)
            worksheet.write(row, colm + 3, ast.asset_seq or '', cell_format_normal)
            worksheet.write(row, colm + 4, ast.name or '', cell_format_normal)
            worksheet.write(row, colm + 5, ast.state or '', cell_format_normal)
            row = row + 1
        row = row + 2
        workbook.close()
        return fp.getvalue()
