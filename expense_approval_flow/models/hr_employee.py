from odoo import api, models, fields,_

class HrEmployeeInherits(models.Model):
    _inherit = 'hr.employee'

    expense_cost = fields.Float("Expense Cost")