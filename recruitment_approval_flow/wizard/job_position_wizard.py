from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from io import BytesIO
import xlsxwriter
import datetime


class JobPositionReport(models.TransientModel):
    _name = 'job.position.report'
    _description = 'Job Position Report'

    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)

    @api.constrains('date_to')
    def _check_date_constraint(self):
        if self.date_to < self.date_from:
            raise ValidationError(_("To date should be greater than From date."))

    def print_pdf_job_position_report(self):
        return self.env.ref("recruitment_approval_flow.action_job_position_pdf_reports").report_action(self)

    def print_xls_job_position_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/job_position_xlsx_report/%s' % (self.id),
            'target': 'new',
        }

    def generate_job_position_report(self, id):
        record = self.env['job.position.report'].sudo().search([('id', '=', id)])

        date_from_str = str(record.date_from)
        date_to_str = str(record.date_to)

        date_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d').date()
        date_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d').date()

        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Sheet 1')
        row = 1

        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 25)
        worksheet.set_column('G:G', 25)


        cell_format_normal = workbook.add_format({'font_size': 12, 'align': 'center'})
        cell_format_emp_details = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        merge_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        merge_format.set_bg_color('#57a0d2')
        merge_format.set_align('vcenter')
        cell_format_emp_details.set_bg_color('#b9bbb6')

        worksheet.merge_range('B1:E1', "Job Position Sheet", merge_format)
        row += 1

        if date_from and date_to:
            job_ids = self.env['hr.job'].sudo().search([('create_date', '>=', date_from), ('create_date', '<=', date_to)])

        row += 1
        colm = 0
        worksheet.write(row, colm, 'Create Date', cell_format_emp_details)
        worksheet.write(row, colm + 1, 'Job Position', cell_format_emp_details)
        worksheet.write(row, colm + 2, 'Department', cell_format_emp_details)
        worksheet.write(row, colm + 3, 'No Of Recruitment', cell_format_emp_details)
        worksheet.write(row, colm + 4, 'Employee Type', cell_format_emp_details)
        worksheet.write(row, colm + 5, 'Recruiter', cell_format_emp_details)
        worksheet.write(row, colm + 6, 'Status', cell_format_emp_details)
        row += 1
        colm = 0
        for job in job_ids:
            formatted_date = job.create_date.strftime('%Y-%m-%d')

            worksheet.set_row(row, 40)
            worksheet.write(row, colm, formatted_date or '', cell_format_normal)
            worksheet.write(row, colm + 1, job.name or '', cell_format_normal)
            worksheet.write(row, colm + 2, job.department_id.name or '', cell_format_normal)
            worksheet.write(row, colm + 3, job.no_of_recruitment or '', cell_format_normal)
            worksheet.write(row, colm + 4, job.contract_type_id.name or '', cell_format_normal)
            worksheet.write(row, colm + 5, job.user_id.name or '', cell_format_normal)
            worksheet.write(row, colm + 6, job.state or '', cell_format_normal)
            row = row + 1
        workbook.close()
        return fp.getvalue()
