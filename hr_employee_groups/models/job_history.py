from odoo import models, fields,api
from dateutil.relativedelta import relativedelta

class JobHistory(models.Model):
    _name = 'job.history'
    _description = 'Employee Job History'

    name = fields.Char("Company Name")
    position = fields.Char("Position")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    experience = fields.Char(string="Experience", compute='_compute_experience', store=True)
    description = fields.Char(string="Description")

    @api.depends('start_date', 'end_date')
    def _compute_experience(self):
        for record in self:
            if record.start_date and record.end_date:
                delta = relativedelta(record.end_date, record.start_date)
                exp_str = ""
                if delta.years:
                    exp_str += str(delta.years) + " Years "
                if delta.months:
                    exp_str += str(delta.months) + " Months "
                if delta.days:
                    exp_str += str(delta.days) + " Days "
                record.experience = exp_str
            else:
                record.experience = "0"
