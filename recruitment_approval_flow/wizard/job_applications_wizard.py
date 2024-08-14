from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from io import BytesIO
import xlsxwriter
import datetime

class JobApplicationReport(models.TransientModel):
    _name = 'job.application.report'
    _description = 'Job Application Report'

    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)

    @api.constrains('date_to')
    def _check_date_constraint(self):
        if self.date_to < self.date_from:
            raise ValidationError(_("To date should be greater than From date."))

    def print_pdf_job_application_report(self):
        return self.env.ref("recruitment_approval_flow.action_job_application_pdf_reports").report_action(self)

    def print_xls_job_application_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/job_application_xlsx_report/%s' % (self.id),
            'target': 'new',
        }

    def generate_job_application_report(self, id):
        record = self.env['job.application.report'].sudo().search([('id', '=', id)])
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
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 40)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 25)
        worksheet.set_column('G:G', 25)
        worksheet.set_column('H:H', 35)
        worksheet.set_column('I:I', 25)

        cell_format_normal = workbook.add_format({'font_size': 12, 'align': 'center'})
        cell_format_emp_details = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        merge_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        merge_format.set_bg_color('#57a0d2')
        merge_format.set_align('vcenter')
        cell_format_emp_details.set_bg_color('#b9bbb6')

        worksheet.merge_range('B1:E1', "Job Application Sheet", merge_format)
        row += 1

        if date_from and date_to:
            application_ids = self.env['hr.applicant'].sudo().search(
                [('create_date', '>=', date_from), ('create_date', '<=', date_to)])

        row += 1
        colm = 0
        worksheet.write(row, colm, 'Create Date', cell_format_emp_details)
        worksheet.write(row, colm + 1, 'Subject', cell_format_emp_details)
        worksheet.write(row, colm + 2, 'Applicant Name', cell_format_emp_details)
        worksheet.write(row, colm + 3, 'Email', cell_format_emp_details)
        worksheet.write(row, colm + 4, 'LinkedIn Profile', cell_format_emp_details)
        worksheet.write(row, colm + 5, 'Degree', cell_format_emp_details)
        worksheet.write(row, colm + 6, 'Mobile', cell_format_emp_details)
        worksheet.write(row, colm + 7, 'Applied Job', cell_format_emp_details)
        worksheet.write(row, colm + 8, 'Status', cell_format_emp_details)
        row += 1
        colm = 0
        for rec in application_ids:
            formatted_date = rec.create_date.strftime('%Y-%m-%d')

            worksheet.set_row(row, 40)
            worksheet.write(row, colm, formatted_date or '', cell_format_normal)
            worksheet.write(row, colm + 1, rec.name or '', cell_format_normal)
            worksheet.write(row, colm + 2, rec.partner_name or '', cell_format_normal)
            worksheet.write(row, colm + 3, rec.email_from or '', cell_format_normal)
            worksheet.write(row, colm + 4, rec.linkedin_profile or '', cell_format_normal)
            worksheet.write(row, colm + 5, rec.type_id.name or '', cell_format_normal)
            worksheet.write(row, colm + 6, rec.partner_mobile or '', cell_format_normal)
            worksheet.write(row, colm + 7, rec.job_id.name or '', cell_format_normal)
            worksheet.write(row, colm + 8, rec.stage_id.name or '', cell_format_normal)
            row = row + 1
        row = row + 2
        workbook.close()
        return fp.getvalue()
