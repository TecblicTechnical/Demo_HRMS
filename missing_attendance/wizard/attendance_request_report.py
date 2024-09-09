from odoo import models, fields,api,_
from io import BytesIO
import xlsxwriter
from odoo.exceptions import ValidationError

class AttendanceRequestReportNew(models.TransientModel):
    _name = 'attendance.request.report'
    _description = "Missing Attendance Request Report"

    def domain_employee_id(self):
        employees = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        if self.env.user.has_group('hr_employee_groups.main_hr_group'):
            employees = self.env['hr.employee'].search([])
        else:
            if self.env.user.has_group('hr_employee_groups.main_manager_group'):
                employees = self.env['hr.employee'].sudo().search(
                    ['|', ('id', '=', self.env.user.employee_id.id), ('parent_id', '=', self.env.user.employee_id.id)])
        return [('id', 'in', employees.ids)]

    employee_id = fields.Many2one('hr.employee', 'Employee', domain=domain_employee_id)
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.today)
    end_date = fields.Date(string="End Date", required=True)

    def get_attendance(self):
        Employee = self.env['hr.employee']
        MissingAttendance = self.env['missing.attendance']

        # Determine employees to consider
        if self.employee_id:
            employees = Employee.browse(self.employee_id.id)
        else:
            if self.env.user.has_group('hr_employee_groups.main_hr_group'):
                employees = Employee.sudo().search([])
            elif self.env.user.has_group('hr_employee_groups.main_manager_group'):
                employees = Employee.sudo().search(['|', ('id', '=', self.env.user.employee_id.id),
                                                    ('parent_id', '=', self.env.user.employee_id.id)])
            else:
                employees = self.env.user.employee_id

        # Define the domain based on the filters
        domain = [('employee_id', 'in', employees.ids)]
        print("domain...............",domain)
        print("employees...............",employees.ids)
        if self.start_date:
            domain.append(('start_date', '>=', self.start_date))
        if self.end_date:
            domain.append(('end_date', '<=', self.end_date))

        # Search for missing attendance records
        missing_attendances = MissingAttendance.search(domain)

        # Prepare the report data
        report_data = []
        for attendance in missing_attendances:
            report_data.append({
                'emp_name': attendance.employee_id.name,
                'date': attendance.start_date.strftime("%d-%m-%Y"),
                'desc': attendance.note,
                'status': attendance.state,
            })

        # Convert the report data into a dictionary
        report_dict = {f"rec_{idx}": rec for idx, rec in enumerate(report_data)}

        return report_dict

    @api.constrains('date_to')
    def _check_date_constraint(self):
        if self.date_to < self.date_from:
            raise ValidationError(_("To date should be greater than From date."))

    def print_report_new(self):
        return self.env.ref('missing_attendance.action_missing_attendance_pdf_new').report_action(self)

    def print_report_xls(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/employee_missing_attendance_xls_report/%s' % (self.id),
            'target': 'new',
        }

    def generate_missing_att_xls_report(self, id):
        record = self.env['attendance.request.report'].sudo().search([('id', '=', id)])
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
        start_date = record.start_date
        end_date = record.end_date

        # Merge and format the cell with the date range
        worksheet.merge_range(
            'A2:D2',
            f'Missing Attendance Report ({start_date} to {end_date})',
            merge_format
        )
        Employee = self.env['hr.employee']
        MissingAttendance = self.env['missing.attendance']
        # Determine employees to consider
        if record.employee_id:
            employees = Employee.browse(record.employee_id.id)
        else:
            if self.env.user.has_group('hr_employee_groups.main_hr_group'):
                employees = Employee.sudo().search([])
            elif self.env.user.has_group('hr_employee_groups.main_manager_group'):
                employees = Employee.sudo().search(['|', ('id', '=', self.env.user.employee_id.id),
                                                    ('parent_id', '=', self.env.user.employee_id.id)])
            else:
                employees = self.env.user.employee_id

        # Define the domain based on the filters
        domain = [('employee_id', 'in', employees.ids)]

        if record.start_date:
            domain.append(('start_date', '>=', record.start_date))
        if record.end_date:
            domain.append(('end_date', '<=', record.end_date))

        # Search for missing attendance records
        missing_attendances = MissingAttendance.search(domain)
        row += 2

        worksheet.write(row, colm, 'Employee Name', cell_format1)
        worksheet.write(row, colm+1, 'Date', cell_format1)
        worksheet.write(row, colm+2, 'Description', cell_format1)
        worksheet.write(row, colm+3, 'Status', cell_format1)

        for att in missing_attendances:
            row += 1
            worksheet.write(row, colm, f"{att.employee_id.name}" ,cell_format2)
            worksheet.write(row, colm + 1, f"{att.start_date.strftime('%d-%m-%Y') or ''}" ,cell_format2)
            worksheet.write(row, colm + 2, f"{att.note or ''}" ,cell_format2)
            worksheet.write(row, colm + 3, f"{att.state}", cell_format2)

        workbook.close()
        return fp.getvalue()
