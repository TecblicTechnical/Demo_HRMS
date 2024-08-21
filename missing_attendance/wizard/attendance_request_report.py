from odoo import models, fields
from io import BytesIO
import datetime
import xlsxwriter
from dateutil.relativedelta import relativedelta


class AttendanceRequestReportNew(models.TransientModel):
    _name = 'attendance.request.report'
    _description = "Missing Attendance Request Report"

    def domain_employee_id(self):
        employees = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        if self.env.user.has_group('hr_employee_groups.main_admin_group'):
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
            if self.env.user.has_group('hr_employee_groups.main_admin_group'):
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

    # def get_attendance(self):
    #     if self.employee_id:
    #         employees = (self.employee_id.id,)
    #     else:
    #         if self.env.user.has_group('employee_work_from_home.group_wfh_hr'):
    #             employees = tuple(self.env['hr.employee'].sudo().search([]).ids)
    #         elif self.env.user.has_group('employee_work_from_home.group_wfh_manager'):
    #             employees = tuple(self.env['hr.employee'].sudo().search(['|', ('id', '=', self.env.user.employee_id.id),
    #                                                                      ('parent_id', '=',
    #                                                                       self.env.user.employee_id.id)]).ids)
    #         else:
    #             employees = (self.env.user.employee_id.id,)
    #     query = """
    #                 SELECT employee_id,start_date,note,state
    #                 FROM missing_attendance
    #                 WHERE (%s IS NULL OR start_date >= %s)
    #                   AND (%s IS NULL OR end_date <= %s)
    #                   AND (employee_id IN %s)
    #
    #             """
    #     self.env.cr.execute(query, (self.start_date, self.start_date, self.end_date, self.end_date,employees))
    #     result = self.env.cr.fetchall()
    #     emp_requests = {r[0]: (r[1], r[2], r[3]) for r in result}
    #     report_data = []
    #     for emp_id,(date,desc,status) in emp_requests.items():
    #         employee = self.env['hr.employee'].browse(emp_id)
    #         report_data.append({
    #              'emp_name': employee.name,
    #              'date': date.strftime("%d-%m-%Y"),
    #              'desc': desc,
    #              'status': status,
    #         })
    #
    #     report_dict = {}
    #     for idx, rec in enumerate(report_data):
    #         report_dict.update({f"rec_{idx}": rec})
    #     return report_dict

    def print_report_new(self):
        return self.env.ref('missing_attendance.action_missing_attendance_pdf_new').report_action(self)

    # def print_report_xls(self):
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': '/web/employee_missing_attendance_report/%s' % (self.id),
    #         'target': 'new',
    #     }
    #
    # def generate_missing_att_report(self, id):
    #     fp = BytesIO()
    #     workbook = xlsxwriter.Workbook(fp)
    #     worksheet = workbook.add_worksheet('Sheet 1')
    #     row = 2
    #     colm = 0
    #     worksheet.set_column('A:A', 30)
    #     worksheet.set_column('B:B', 30)
    #     worksheet.set_column('C:C', 30)
    #     worksheet.set_column('D:D', 30)
    #
    #     cell_format1 = workbook.add_format({'bold': True, 'font_size': 14,'align':'center','border': 1})
    #     cell_format2 = workbook.add_format({'font_size':12,'align':'center'})
    #     cell_format1.set_bg_color('yellow')
    #     merge_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
    #     merge_format.set_bg_color('#57a0d2')
    #     merge_format.set_align('vcenter')
    #
    #     worksheet.merge_range('A2:D2', employee_period_type.capitalize() + ' Period Details ', merge_format)
    #
    #     employee_ids = self.env['hr.employee'].sudo().search([('employee_period_type','=', employee_period_type)])
    #     row += 2
    #
    #     worksheet.write(row, colm, 'Employee Name', cell_format1)
    #     worksheet.write(row, colm+1, 'Joining Date', cell_format1)
    #     worksheet.write(row, colm+2, 'Completion Date', cell_format1)
    #     worksheet.write(row, colm+3, 'Remaining Days', cell_format1)
    #
    #     for emp in employee_ids:
    #         row += 1
    #
    #         delta = relativedelta(emp.completion_date, datetime.date.today())
    #         remaining_days_year = ((str(delta.years) + " year, ") if delta.years else '') + ((str(delta.months) + " months,") if delta.months else '') + ((str(delta.days) + " days") if delta.days else '')
    #
    #         worksheet.write(row, colm, f"{emp.name}" ,cell_format2)
    #         worksheet.write(row, colm+1, f"{emp.joining_date.strftime('%d-%m-%Y') or ''}" ,cell_format2)
    #         worksheet.write(row, colm+2, f"{emp.completion_date.strftime('%d-%m-%Y') or ''}" ,cell_format2)
    #         worksheet.write(row, colm + 3, f"{remaining_days_year}", cell_format2)
    #
    #     workbook.close()
    #     return fp.getvalue()
