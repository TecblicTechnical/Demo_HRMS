from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError

class HrExpenseInherits(models.Model):
    _inherit = 'hr.expense'

    employee_expense_cost = fields.Float("Maximum Employee Expense Cost")

    @api.constrains('product_id', 'unit_amount')
    def _check_standard_amount(self):
        for expense in self:
            print("expense...........",expense)
            if expense.product_id and expense.product_id.standard_price < expense.unit_amount:
                raise ValidationError("The unit amount of the expense cannot be greater than the standard amount !!!")