# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from io import BytesIO
import xlsxwriter
from datetime import timedelta

class EquipmentAssetReport(models.TransientModel):
    _name = 'equipment.asset.report'
    _description = 'Equipment Asset Report'

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    department_ids = fields.Many2many('hr.department', string='Department')
    company_id = fields.Many2one(
        'res.partner',
        string='B2B Company',
        domain=lambda self: [('category_id', '=', self.env.ref('asset_management.b2b_category_tag').id)]
    )

    def print_asset_report_pdf(self):
        return self.env.ref("asset_management.action_employee_equipment_pdf_report").report_action(self)

    def print_asset_report_xls(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/employee_equipment_xlsx_report/%s' % (self.id),
            'target': 'new',
        }

    def generate_emp_asset_report(self, id):
        record = self.env['equipment.asset.report'].sudo().search([('id', '=', id)])

        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Sheet 1')
        row = 1
        colm = 0

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 30)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 30)

        cell_format_normal = workbook.add_format({'font_size': 12, 'align': 'center'})
        cell_format_emp_details = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        merge_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        merge_format.set_bg_color('#57a0d2')
        merge_format.set_align('vcenter')
        cell_format_emp_details.set_bg_color('#b9bbb6')

        worksheet.merge_range('B1:E1', "Employee Asset Sheet", merge_format)
        row += 1

        if record.employee_ids or record.department_ids:
            asset_ids = self.env['maintenance.equipment'].sudo().search(
                ['|',('employee_id', 'in', record.employee_ids.ids), ('department_id', 'in', record.department_ids.ids)])
        else:
            asset_ids = self.env['maintenance.equipment'].sudo().search([])

        row += 1
        colm = 0
        worksheet.write(row, colm, 'Asset Company Name', cell_format_emp_details)
        worksheet.write(row, colm + 1, 'Asset Code', cell_format_emp_details)
        worksheet.write(row, colm + 2, 'Category', cell_format_emp_details)
        worksheet.write(row, colm + 3, 'Assign Date', cell_format_emp_details)
        worksheet.write(row, colm + 4, 'Employee', cell_format_emp_details)
        worksheet.write(row, colm + 5, 'Department', cell_format_emp_details)
        worksheet.write(row, colm + 6, 'Device Company', cell_format_emp_details)
        worksheet.write(row, colm + 7, 'Password', cell_format_emp_details)
        worksheet.write(row, colm + 8, 'Status', cell_format_emp_details)
        row += 1
        colm = 0
        for ast in asset_ids:
            formatted_date = str(ast.assign_date)

            worksheet.set_row(row, 40)
            worksheet.write(row, colm, ast.name or '', cell_format_normal)
            worksheet.write(row, colm+1, ast.sequence or '', cell_format_normal)
            worksheet.write(row, colm+2, ast.category_id.name or '', cell_format_normal)
            worksheet.write(row, colm+3, formatted_date or '', cell_format_normal)
            worksheet.write(row, colm+4, ast.employee_id.name or '', cell_format_normal)
            worksheet.write(row, colm+5, ast.department_id.name or '', cell_format_normal)
            worksheet.write(row, colm+6, ast.device_company.name or '', cell_format_normal)
            worksheet.write(row, colm+7, ast.password_of_device or '', cell_format_normal)
            worksheet.write(row, colm+8, ast.state or '', cell_format_normal)
            row = row + 1
        row = row + 2
        workbook.close()
        return fp.getvalue()
