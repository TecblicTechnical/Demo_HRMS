from odoo import api, models, fields,_

class HrEmployeePublicInherits(models.Model):
    _inherit = "hr.employee.public"

    expense_cost = fields.Float("Expense Cost",store=True)