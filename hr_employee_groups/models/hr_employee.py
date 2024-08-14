from odoo import api, models, fields,_
from dateutil.relativedelta import relativedelta
from datetime import datetime

class EmployeeInherit(models.Model):
    _inherit = "hr.employee"

    upload_document_ids = fields.One2many('hr.employee.document','employee_id',string="Document Upload")
    job_history_ids = fields.One2many("job.history",'employee_id',string="Job History")
    active = fields.Boolean('Active', related='', default=True, store=True, readonly=False)

    name_as_per_bank = fields.Char("Name As Per Bank")
    checkout_selection = fields.Selection([('automatic', 'Automatic'), ('manually', 'Manually')], default='automatic')
    employee_period_duration = fields.Integer('Employee Training Period Duration', default=6)
    employee_probabtion_period_duration = fields.Integer('Employee Probabtion Period Duration', default=6)
    employee_period_type = fields.Selection(
        [('trainee', 'Trainee'), ('probation', 'Probation'), ('permanent', 'Permanent'), ('notice', 'Notice'),
         ('other', 'Other')], 'Employee Period')
    joining_date = fields.Date('Joining Date')
    completion_date = fields.Date('Training Completion Date')
    probabtion_completion_date = fields.Date('Probabtion Completion Date')
    employee_leave = fields.Integer('Employee Leave')
    uan_number = fields.Char('UAN Number')
    bank_ac_no = fields.Char('Bank A/C No')
    bank_name = fields.Char('Bank Name')
    bank_ifsc_code = fields.Char('IFSC Code')
    street = fields.Char(related='address_home_id.street', string="Street")
    street2 = fields.Char(related='address_home_id.street2', string="Street2")
    city = fields.Char(related='address_home_id.city', string="City")
    state_id = fields.Many2one(related='address_home_id.state_id', string="State")
    country_id = fields.Many2one(related='address_home_id.country_id', string="Country")
    project_department_id = fields.Many2many('hr.department', 'dep_rel', 'hr_emp_rel', string='Project Department')
    career_start_date = fields.Date('Career Start Date')
    total_experience = fields.Char('Total Experience', compute='total_experience_count')
    personal_email_new = fields.Char(string=" Email")
    paid_leave_balance = fields.Float('Paid Leaves', compute='paid_leave_balance_count', help="Remaining Paid Leaves")
    is_permanent_emp = fields.Boolean("Is Permanent employee")

    def paid_leave_balance_count(self):
        for rec in self:
            rec.paid_leave_balance = rec.remaining_leaves


    def action_archive(self):
        res = super().action_archive()
        for rec in self:
            timesheets = self.env['account.analytic.line'].search([('employee_id', '=', rec.id)])
            timesheets.write({'active': False})
            missing_attedence = self.env['missing.attendance'].search([('employee_id', '=', rec.id)])
            missing_attedence.write({'active': False})
            employee_attedence = self.env['hr.attendance'].search([('employee_id', '=', rec.id)])
            employee_attedence.write({'active': False})
            employee_leave = self.env['hr.leave'].search([('employee_id', '=', rec.id)])
            employee_leave.write({'active': False})
            employee_wfh = self.env['employee.work.from.home'].search([('employee_id', '=', rec.id)])
            employee_wfh.write({'active': False})
            employee_eraly_leave = self.env['employee.early.leave'].search([('employee_id', '=', rec.id)])
            employee_eraly_leave.write({'active': False})
        return res

    def action_unarchive(self):
        res = super().action_unarchive()
        for rec in self:
            timesheets = self.env['account.analytic.line'].search([('active','=',False),('employee_id','=', rec.id)])
            timesheets.sudo().write({'active': True})
            missing_attedence = self.env['missing.attendance'].search([('active','=',False),('employee_id','=', rec.id)])
            missing_attedence.sudo().write({'active': True})
            employee_attedence = self.env['hr.attendance'].search([('active','=',False),('employee_id','=', rec.id)])
            employee_attedence.write({'active': True})
            employee_leave = self.env['hr.leave'].search([('active','=',False),('employee_id','=', rec.id)])
            employee_leave.write({'active': True})
            employee_wfh = self.env['employee.work.from.home'].search([('active','=',False),('employee_id','=', rec.id)])
            employee_wfh.write({'active': True})
            employee_eraly_leave = self.env['employee.early.leave'].search([('active','=',False),('employee_id','=', rec.id)])
            employee_eraly_leave.write({'active': True})
        return res

    @api.depends('career_start_date')
    def total_experience_count(self):
        for rec in self:
            today = datetime.now().date()
            delta = relativedelta(today, rec.career_start_date)
            # rec.total_experience = str(delta.years)+" Years"+" "+str(delta.months)+" Months"
            rec.total_experience = str(delta.years) + "." + str(delta.months) + " Years"

    @api.onchange('joining_date', 'employee_period_duration')
    def onchnage_joining_date(self):
        for rec in self:
            if rec.joining_date:
                six_months_date = rec.joining_date + relativedelta(months=+rec.employee_period_duration)
                rec.completion_date = six_months_date
                # if rec.completion_date:
                #     rec.completion_date = six_months_date

    @api.onchange('employee_period_type', 'employee_probabtion_period_duration')
    def onchnage_probabtion_duration(self):
        for rec in self:
            if rec.employee_period_type == 'probation':
                if rec.completion_date:
                    six_months_date = rec.completion_date + relativedelta(
                        months=+rec.employee_probabtion_period_duration)
                    rec.probabtion_completion_date = six_months_date
                    # if rec.completion_date:
                else:
                    six_months_date = rec.joining_date + relativedelta(months=+rec.employee_probabtion_period_duration)
                    rec.probabtion_completion_date = six_months_date
                #     rec.completion_date = six_months_date

    def employee_period_completion_mail_cron(self):
        employee_ids = self.env['hr.employee'].sudo().search(
            [('employee_period_type', 'in', ('trainee', 'probation'))])
        for employee_id in employee_ids:
            if employee_id.completion_date == datetime.date.today():
                if employee_id.employee_period_type == 'trainee':
                    employee_id.employee_period_type = 'probation'
            if employee_id.probabtion_completion_date == datetime.date.today():
                if employee_id.employee_period_type == 'probation':
                    employee_id.employee_period_type = 'permanent'
            week_ago = employee_id.completion_date - datetime.timedelta(days=7)
            two_week_ago = employee_id.completion_date - datetime.timedelta(days=15)
            if datetime.date.today() in [week_ago, two_week_ago]:
                mail = self.env['mail.mail']
                mail_data = {'subject': 'Completion period',
                             'body_html': 'This is to inform you that ' + str(
                                 employee_id.employee_period_type) + ' period of ' + str(
                                 employee_id.name) + '  will be completed on this date : ' + str(
                                 employee_id.completion_date) + '.' + '<br/> As he/she joined on ' + str(
                                 employee_id.joining_date) + " he will complete his/her " + str(
                                 employee_id.employee_period_duration) + ' month on the mentioned date.',
                             'email_from': 'hr@tecblic.com',
                             'email_to': 'hr@tecblic.com'
                             }
                mail_out = mail.create(mail_data)
                mail_out.sudo().send()