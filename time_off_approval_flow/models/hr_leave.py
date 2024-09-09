from odoo import api, models, fields, _
from odoo.tools import float_round,float_compare, format_date
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, date

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    check_manager = fields.Boolean("Is Manager", compute='check_is_manager', default=True)
    active = fields.Boolean(string='Active', required=True, index=True, default=True, )
    approve_button_hide = fields.Boolean(compute="compute_approve_button_hide")

    def check_is_manager(self):
        for rec in self:
            is_self = rec.employee_id and rec.employee_id.user_id and rec.employee_id.user_id.id == rec.env.user.id and not self.env.user.has_group("hr_employee_groups.main_hr_group")
            if is_self:
                rec.check_manager = True
            else:
                rec.check_manager = False


    def send_to_manager(self, email, rec_id):
        users_in_group = self.env['res.users'].sudo().search([('groups_id.name', '=', 'HR')])
        employees_in_group = users_in_group.mapped('employee_ids')
        hr_emails = employees_in_group.mapped('work_email')
        print("hr_emails..............",hr_emails)

        template_values = {
            'email_cc': email,
            'email_to': hr_emails,
        }
        for_manager = for_hr = False
        if self.env.context.get('for_manager'):
            for_manager = True
        if self.env.context.get('for_hr'):
            for_hr = True
        template = self.env.ref('time_off_approval_flow.employee_attendance_leave_request_mail',
                                raise_if_not_found=False)
        template.write(template_values)
        template = template.with_context(for_manager=for_manager, for_hr=for_hr)
        template.sudo().send_mail(rec_id, force_send=True)
        self.write({'state': 'manager_approval'})
        return True

    def compute_approve_button_hide(self):
        for rec in self:
            rec.approve_button_hide = False
            if rec.env.user.employee_id.id == rec.employee_id.id and not self.env.user.has_group("employee_work_from_home.group_wfh_hr"):
                rec.approve_button_hide = True

    @api.constrains('number_of_days', 'holiday_status_id')
    def _check_holidays(self):
        paid_id = self.env['hr.leave.type'].sudo().search([('code', '=', 'Paid')], limit=1)
        take_leave = float_round(self.employee_id.allocation_count - self.employee_id.remaining_leaves, precision_digits=2)

        allocation = float(self.employee_id.allocation_display)

        pending = allocation - take_leave
        if self.holiday_status_id == paid_id and pending < self.number_of_days :
            raise ValidationError(_('You cannot create leave more then remaining balance'))

        mapped_days = self.mapped('holiday_status_id').get_employees_days(self.mapped('employee_id').ids)
        for holiday in self:
            if holiday.holiday_type != 'employee' or not holiday.employee_id or holiday.holiday_status_id.requires_allocation == 'no':
                continue
            leave_days = mapped_days[holiday.employee_id.id][holiday.holiday_status_id.id]
            remaining = float_round(paid_id.virtual_remaining_leaves, precision_digits=2) or 0.0
            if remaining > 0.25 and holiday.holiday_status_id == paid_id:
                if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or float_compare(
                        leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                    raise ValidationError(_('The number of remaining time off is not sufficient for this time off type.\n'
                                            'Please also check the time off waiting for validation.'))
            if self.request_date_from and self.request_date_to and self.request_date_from.month != self.request_date_to.month:
                raise ValidationError(_('You are not able to create two month combine leave.\n'
                                        'from and to date should be in same month.'))

    # @api.model
    # def create(self, vals):
    #     res = super(HrLeave, self).create(vals)
    #     hr = self.env['res.users'].sudo().search([]).filtered(
    #         lambda a: a.has_group('hr_employee_groups.main_hr_group'))
    #     if res.employee_id.parent_id:
    #         start_time = datetime.combine(res.create_date.date(), res.create_date.min.time())
    #         end_time = datetime.combine(res.create_date.date(), res.create_date.max.time())
    #         leaves = self.env['hr.leave'].sudo().search([('state','=','validate'),('employee_id', '=', res.employee_id.parent_id.id), ('request_date_from', '>=', start_time),('request_date_from', '<=', end_time),('request_date_to', '>=', start_time),('request_date_to', '<=', end_time)])
    #         if leaves:
    #             if res.employee_id.parent_id.parent_id:
    #                 manager_leaves = self.env['hr.leave'].sudo().search([('state','=','validate'),('employee_id', '=', res.employee_id.parent_id.parent_id.id),
    #                                                              ('request_date_from', '>=', start_time),
    #                                                              ('request_date_from', '<=', end_time),
    #                                                              ('request_date_to', '>=', start_time),
    #                                                              ('request_date_to', '<=', end_time)])
    #                 if manager_leaves:
    #                     if hr:
    #                         self.with_context(for_hr=True).send_to_manager(hr.work_email, res.id)
    #                 else:
    #                     # Manager Head
    #                     self.with_context(for_manager=True).send_to_manager(res.employee_id.parent_id.parent_id.work_email, res.id)
    #             else:
    #                 if hr:
    #                     self.with_context(for_hr=True).send_to_manager(hr.work_email, res.id)
    #         else:
    #             self.sudo().send_to_manager(res.employee_id.parent_id.work_email, res.id)
    #     else:
    #         if hr:
    #             self.sudo().send_to_manager(hr.work_email, res.id)
    #     return res

    @api.model
    def create(self, vals):
        res = super(HrLeave, self).create(vals)

        # Use sudo to ensure access to HR users
        hr = self.env['res.users'].sudo().search([]).filtered(
            lambda a: a.has_group('hr_employee_groups.main_hr_group')
        )

        if res.employee_id.parent_id:
            # Use sudo to access employee's parent and related leave records
            parent_employee = res.employee_id.parent_id.sudo()
            start_time = datetime.combine(res.create_date.date(), res.create_date.min.time())
            end_time = datetime.combine(res.create_date.date(), res.create_date.max.time())

            # Use sudo to search for leaves of the parent employee
            leaves = self.env['hr.leave'].sudo().search([
                ('state', '=', 'validate'),
                ('employee_id', '=', parent_employee.id),
                ('request_date_from', '>=', start_time),
                ('request_date_from', '<=', end_time),
                ('request_date_to', '>=', start_time),
                ('request_date_to', '<=', end_time)
            ])

            if leaves:
                # Use sudo to access parent of the parent employee
                if parent_employee.parent_id:
                    grandparent_employee = parent_employee.parent_id.sudo()

                    # Use sudo to search for leaves of the grandparent employee
                    manager_leaves = self.env['hr.leave'].sudo().search([
                        ('state', '=', 'validate'),
                        ('employee_id', '=', grandparent_employee.id),
                        ('request_date_from', '>=', start_time),
                        ('request_date_from', '<=', end_time),
                        ('request_date_to', '>=', start_time),
                        ('request_date_to', '<=', end_time)
                    ])

                    if manager_leaves:
                        if hr:
                            self.with_context(for_hr=True).sudo().send_to_manager(hr.work_email, res.id)
                    else:
                        # Manager Head
                        self.with_context(for_manager=True).sudo().send_to_manager(grandparent_employee.work_email,
                                                                                   res.id)
                else:
                    if hr:
                        self.with_context(for_hr=True).sudo().send_to_manager(hr.work_email, res.id)
            else:
                self.sudo().send_to_manager(parent_employee.work_email, res.id)
        else:
            if hr:
                self.sudo().send_to_manager(hr.work_email, res.id)

        return res

