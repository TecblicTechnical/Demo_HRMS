from odoo import api, models, fields,_
from dateutil.relativedelta import relativedelta
from datetime import datetime


class PublicEmployeeInherit(models.Model):
    _inherit = "hr.employee.public"

    upload_document_ids = fields.One2many('hr.employee.document','employee_id',string="Document Upload")
    job_history_ids = fields.One2many("job.history",'employee_id',string="Job History")

    # private partner
    personal_email_new = fields.Char(string=" Email")
    employee_period_duration = fields.Integer('Employee Training Period Duration', default=6)
    employee_probabtion_period_duration = fields.Integer('Employee Probabtion Period Duration', default=6)
    employee_period_type = fields.Selection(
        [('trainee', 'Trainee'), ('probation', 'Probation'), ('permanent', 'Permanent'), ('other', 'Other')],
        'Employee Period')
    joining_date = fields.Date('Joining Date')
    completion_date = fields.Date('Training Completion Date')
    probabtion_completion_date = fields.Date('Probabtion Completion Date')
    employee_leave = fields.Integer('Employee Leave')
    uan_number = fields.Char('UAN Number')
    bank_ac_no = fields.Char('Bank A/C No')
    bank_name = fields.Char('Bank Name')
    name_as_per_bank = fields.Char("Name As Per Bank")
    bank_ifsc_code = fields.Char('IFSC Code')
    project_department_id = fields.Many2many('hr.department', 'dep_rel', 'hr_emp_rel', string='Project Department')
    address_home_id = fields.Many2one('res.partner', 'Address')
    private_email = fields.Char(related='address_home_id.email', string="Private Email")
    phone = fields.Char(related='address_home_id.phone', string="Private Phone")
    street = fields.Char(related='address_home_id.street', string="Street")
    street2 = fields.Char(related='address_home_id.street2', string="Street2")
    city = fields.Char(related='address_home_id.city', string="City")
    state_id = fields.Many2one(related='address_home_id.state_id', string="State")
    country_id = fields.Many2one(related='address_home_id.country_id', string="Country")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    birthday = fields.Date('Date of Birth')
    emergency_contact = fields.Char("Emergency Contact")
    career_start_date = fields.Date('Career Start Date')
    total_experience = fields.Char('Total Experience', compute='total_experience_count')
    is_permanent_emp = fields.Boolean("Is Permanent Employee")
    paid_leave_balance = fields.Float('Paid Leaves', compute='paid_leave_balance_count', help="Remaining Paid Leaves")


    @api.depends('career_start_date')
    def total_experience_count(self):
        for rec in self:
            today = datetime.now().date()
            delta = relativedelta(today, rec.career_start_date)
            rec.total_experience = str(delta.years) + "." + str(delta.months) + " Years"

    def paid_leave_balance_count(self):
        for rec in self:
            rec.paid_leave_balance = rec.remaining_leaves
















