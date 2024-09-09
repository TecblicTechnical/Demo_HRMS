from odoo import models, fields, api, _,tools
from datetime import datetime, date
from odoo.exceptions import ValidationError, UserError

class LeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    active = fields.Boolean('Active',default=True, tracking=True)

    @api.model
    def create(self, vals):
        res = super(LeaveAllocation, self).create(vals)
        if self._context.get("create_allocation", False):
            res.update({'create_date': self.env.cr.execute(
                "UPDATE hr_leave_allocation set create_date = '%s' WHERE id=%s" % (
                self._context.get("allocate_create_date"), res.id))
                        })
        return res

    def description_change(self):
        for record in self:
            desc = 'Balance as of ' + date.today().strftime('%B') + " " + date.today().strftime(
                '%Y') + " for " + record.employee_id.name
            if record.name != desc:
                record.write({'name': desc})

    def action_approve(self):
        res = super(LeaveAllocation, self).action_approve()

        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        if self.env.user.employee_id.id == self.employee_id.id:
            raise UserError(_('Only manager can approve'))
        if self.env.user.employee_id.id == self.employee_id.parent_id.id:
            # rec.approve_button_hide = False
            for holiday in self:
                if not holiday.name:
                    holiday.name = "Balance as of January " + str(datetime.date.today().year) + " for " + (
                            holiday.employee_id and holiday.employee_id.name or '')
                if holiday.state == 'validate':
                    raise UserError(_('Allocation request must be confirmed ("To Approve") in order to approve it.'))
                elif holiday.state in ['validate1']:
                    holiday.action_validate()
                    holiday.activity_update()
                elif holiday.state in ['draft', 'confirm']:
                    current_employee = self.env.user.employee_id
                    holiday.filtered(lambda hol: hol.validation_type == 'both').write(
                        {'state': 'validate1', 'first_approver_id': current_employee.id})
                    # self.filtered(lambda hol: hol.validation_type == 'both').write({'state': 'validate', 'second_approver_id': current_employee.id})
                    holiday.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
                    # self.action_validate()
                    holiday.activity_update()
        return res
