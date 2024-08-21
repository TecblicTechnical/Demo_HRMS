from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, date, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
import werkzeug.urls
from dateutil.relativedelta import relativedelta
import calendar


class MissingAttendance(models.Model):
    _name = 'missing.attendance'
    _description = 'Missing Attendance'
    _rec_name = 'employee_id'
    _order = 'id desc'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    def domain_employee_id(self):
        employees = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        if self.env.user.has_group('hr_employee_groups.main_admin_group'):
            employees = self.env['hr.employee'].search([])
        else:
            if self.env.user.has_group('hr_employee_groups.main_manager_group'):
                employees = self.env['hr.employee'].sudo().search(
                    ['|', ('id', '=', self.env.user.employee_id.id), ('parent_id', '=', self.env.user.employee_id.id)])
        return [('id', 'in', employees.ids)]

    def _default_employee(self):
        return self.env.user.employee_id

    employee_id = fields.Many2one('hr.employee', string='Employee', domain=domain_employee_id,
                                  default=_default_employee)
    company_id = fields.Many2one('res.company', string='Company')
    manager_id = fields.Many2one('hr.employee', string='Manager')
    # manager_id = fields.Many2one(related='employee_id.parent_id', readonly=False, string='Manager')
    request_type = fields.Selection([('office', 'OFFICE'), ('on site', 'ON SITE'), ('wfh', 'WFH')],
                                    string='Request Type', default='office', required=1)
    start_date = fields.Datetime("Start Date")
    end_date = fields.Datetime('End Date')
    state = fields.Selection(selection=[('draft', 'Draft'), ('manager_approval', 'Manager Approval'),
                                        ('hr_approval', 'HR Approval'), ('approved', 'Approved'),
                                        ('reject', 'Rejected')],
                             string='Status', readonly=True, copy=False, default='draft')
    note = fields.Text('Description')
    attendance_ids = fields.Many2many('hr.attendance', string='Attendance')
    attendance_history_ids = fields.One2many('missing.attendance.history', 'attendance_history_id', string='Attendance')
    approval_url = fields.Char(compute='_compute_approval_url', string='Approval Email URL')
    active = fields.Boolean(string='Active', required=True, index=True, default=True, )
    # approve_button_hide = fields.Boolean()
    approve_button_hide = fields.Boolean(compute="compute_approve_button_hide")

    def compute_approve_button_hide(self):
        for rec in self:
            rec.approve_button_hide = False
            if self.env.user.employee_id.id == self.employee_id.id and not self.env.user.has_group(
                    "hr_employee_groups.main_admin_group"):
                rec.approve_button_hide = True
            if self.env.user.employee_id.id == self.employee_id.parent_id.id:
                rec.approve_button_hide = False

    def _compute_approval_url(self):
        result = self.sudo()._get_approval_url_for_action()
        for app in self:
            app.approval_url = result.get(app.id, False)

    def _get_approval_url_for_action(self, action=None, view_type=None, menu_id=None, res_id=None, model=None):
        res = dict.fromkeys(self.ids, False)
        for app in self:
            base_url = self.env.user.get_base_url()
            menu_id = self.env.ref('missing_attendance.menu_missing_attendance_root', False).id
            action_id = self.env.ref('missing_attendance.missing_attendance_action', False).id
            approval_url = "/web/#id=%s&action=%s&model=missing.attendance&view_type=form&cids=1&menu_id=%s" % (
            self.id, action_id, menu_id)
            approval_url = werkzeug.urls.url_join(base_url, approval_url)
            res[app.id] = approval_url
        return res

    @api.constrains('start_date')
    def _check_date_constraint(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError(_("End Date cannot be smaller than Start date"))
            if self.end_date.date() != self.start_date.date() and self.request_type != 'on site':
                raise ValidationError(_("Start and End Date must be same"))
            if self.employee_id:
                attendance_ids = self.env['hr.attendance'].sudo().search(
                    [('employee_id', '=', self.employee_id.id)]).filtered(lambda
                                                                              a: a.check_in and self.start_date and a.check_out and self.end_date and a.check_in.date() >= self.start_date.date() and a.check_out.date() <= self.end_date.date())
                self.attendance_ids = [(6, 0, attendance_ids.ids)]

        end_of_month = self.start_date.replace(day=calendar.monthrange(self.start_date.year, self.start_date.month)[1])
        current_date = datetime.now()
        print("....end_of_month...", end_of_month)
        print("....current_date...", current_date)
        if current_date.date() > end_of_month.date():
            raise ValidationError(_("You Can create Missing Attendance of current month only."))
        if self.start_date.date() > current_date.date():
            raise ValidationError(_("Start Date cannot be greater than today's date."))

    @api.model
    def default_get(self, fields):
        vals = super(MissingAttendance, self).default_get(fields)
        in_time = datetime.strptime('10' + '00', '%H%M').time()
        out_time = datetime.strptime('19' + '00', '%H%M').time()
        checkin = datetime.combine(datetime.today(), in_time)
        checkout = datetime.combine(datetime.today(), out_time)

        checkin = checkin.strptime(str(checkin), DEFAULT_SERVER_DATETIME_FORMAT)
        checkout = checkout.strptime(str(checkout), DEFAULT_SERVER_DATETIME_FORMAT)
        now = datetime.now()
        now_utc = pytz.utc.localize(now)
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        now_tz = now_utc.astimezone(tz)
        check_in_tz = now_tz + relativedelta(year=checkin.year, month=checkin.month, day=checkin.day,
                                             hour=checkin.hour, minute=checkin.minute,
                                             second=checkin.second, microsecond=0)
        check_in_tz_naive = check_in_tz.astimezone(pytz.utc).replace(tzinfo=None)

        check_out_tz = now_tz + relativedelta(year=checkout.year, month=checkout.month,
                                              day=checkout.day, hour=checkout.hour,
                                              minute=checkout.minute, second=checkout.second,
                                              microsecond=0)
        check_out_tz_naive = check_out_tz.astimezone(pytz.utc).replace(tzinfo=None)
        if self.env.user.employee_id.id == vals.get("employee_id"):
            vals.update({
                'approve_button_hide': True,
            })
        else:
            vals.update({
                'approve_button_hide': False,
            })

        vals.update({
            'start_date': check_in_tz_naive,
            'end_date': check_out_tz_naive,
        })
        return vals

    @api.onchange('employee_id', 'end_date', 'request_type')
    def oncahnge_employee_id(self):
        if self.employee_id and self.employee_id.parent_id:
            self.manager_id = self.employee_id.parent_id.id
        else:
            self.manager_id = False
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError(_("End Date cannot be smaller than Start date"))
            if self.end_date.date() != self.start_date.date() and self.request_type != 'on site':
                raise ValidationError(_("Start and End Date must be same"))
            if self.employee_id and self.end_date and self.start_date:
                attendance_ids = self.env['hr.attendance'].sudo().search([('employee_id', '=', self.employee_id.id)],
                                                                         limit=1)
                id_list = []
                for loop in attendance_ids:
                    if loop.check_in and loop.check_out and loop.check_in.date() <= self.start_date.date() and loop.check_out.date() >= self.end_date.date():
                        id_list.append(loop.id)
                self.attendance_ids = [(6, 0, id_list)]

    @api.onchange('attendance_ids')
    def oncahnge_attendance_ids(self):
        if self.attendance_ids:
            vals = self.attendance_history_ids.create({
                'employee_id': self.employee_id.id,
                'check_in': self.attendance_ids.check_in,
                'check_out': self.attendance_ids.check_out
            })
            self.write({
                'attendance_history_ids': [
                    (6, 0, vals.ids)]
            })

    def set_manager_approve(self):
        for record in self:
            record.write({'state': 'manager_approval'})
            # hr = self.env['res.users'].sudo().search([]).filtered(
            #     lambda a: a.has_group('employee_work_from_home.group_wfh_hr'))
            template_values = {
                'email_cc': 'hr@tecblic.com',
            }
            template = self.env.ref('missing_attendance.missing_attendance_request_email_template',
                                    raise_if_not_found=False)
            template.write(template_values)
            template.sudo().send_mail(record.id, force_send=True)
        return True

    def set_hr_approve(self):
        is_manager = self.env.user.has_group('hr_employee_groups.main_manager_group')
        is_hr = self.env.user.has_group('hr_employee_groups.main_admin_group')
        for record in self:
            if is_manager or is_hr and record.state == 'manager_approval':
                record.write({'state': 'hr_approval'})
                # hr = self.env['res.users'].sudo().search([]).filtered(
                #     lambda a: a.has_group('employee_work_from_home.group_wfh_hr'))
                template_values = {
                    'email_to': 'hr@tecblic.com',
                }
                template = self.env.ref('missing_attendance.missing_attendance_request_email_template_for_hr',
                                        raise_if_not_found=False)
                template.write(template_values)
                template.sudo().send_mail(record.id, force_send=True)
            else:
                raise UserError("You are not allowed to approve missing attendance that should be approved by Manager")

        return True

    def set_approved(self):
        is_hr = self.env.user.has_group('hr_employee_groups.main_admin_group')
        for record in self:
            if is_hr and record.state == 'hr_approval':
                attendance_id = self.env['hr.attendance']
                exiting_attendance_id = attendance_id.sudo().search([('employee_id','=',record.employee_id.id)]).filtered(lambda a:a.check_in and  a.check_out and a.check_in.date() >= record.start_date.date() and a.check_out.date() <= record.end_date.date()).sorted(key=lambda a:a.check_in.date())
                print("exiting_attendance_id.....",exiting_attendance_id)
                # exiting_attendance_id = attendance_id.sudo().search([('employee_id','=',record.employee_id.id)]).filtered(lambda a:a.check_in.date() == record.start_date.date() and a.check_out.date() == record.end_date.date())
                days = set(
                    [
                        calendar.day_name[int(each.dayofweek)]
                        for each in record.employee_id.resource_calendar_id.attendance_ids
                    ]
                )
                if not exiting_attendance_id:
                    if record.request_type != 'on site':
                        if record.start_date.strftime("%A") in days:
                            attendance_id.sudo().create({'employee_id': record.employee_id.id,
                                                         'check_in': record.start_date,
                                                         'check_out': record.end_date})
                        else:
                            raise ValidationError(_("You Can't Create Attendance on week of day"))
                    else:
                        print("exiting_attendance_id.....", exiting_attendance_id)

                        out_time = record.end_date.time()
                        in_time = record.start_date.time()
                        start_date = record.start_date
                        last_date = datetime.combine(start_date, out_time)
                        day_diff = (record.end_date.date() - record.start_date.date()).days + 1
                        count = 1
                        for day in range(day_diff):
                            if start_date.strftime("%A") in days:
                                attendance_id.sudo().create({'employee_id': record.employee_id.id,
                                                             'check_in': start_date,
                                                             'check_out': last_date})
                            next_date_in = record.start_date.date() + timedelta(days=count)
                            next_date_out = record.start_date.date() + timedelta(days=count)
                            start_date = datetime.combine(next_date_in, in_time)
                            last_date = datetime.combine(next_date_out, out_time)
                            count += 1
                else:
                    out_time = record.end_date.time()
                    in_time = record.start_date.time()
                    start_date = record.start_date
                    for rec in exiting_attendance_id:
                        print("rec..222222222...", rec)
                        # update_checkout = self.env['hr.attendance'].search([('id','=',rec.id)])
                        # print("update_checkout..........",update_checkout)
                        print("rec.checkout..........",rec.check_out)
                        print("rec.checkin..........",rec.check_in)
                        self.env['hr.attendance'].sudo().create({
                            'employee_id': record.employee_id.id,
                            'check_in': start_date,
                            'check_out': datetime.combine(start_date.date(), out_time)
                        })
                        print("Created new attendance...........")
                        start_date = datetime.combine(start_date.date() + timedelta(days=1), in_time)
                record.write({'state': 'approved'})
                template = self.env.ref('missing_attendance.missing_attendance_request_email_template_approved',
                                        raise_if_not_found=False)
                template.sudo().send_mail(record.id, force_send=True)
            else:
                raise UserError("You are not allowed to approve leaves that should be approved by HR")

        return True

    def set_reject(self):
        for record in self:
            record.write({'state': 'reject'})
            template = self.env.ref('missing_attendance.missing_attendance_request_email_template_reject',
                                    raise_if_not_found=False)
            template.sudo().send_mail(record.id, force_send=True)
        return True

    def set_reset_to_draft(self):
        for record in self:
            record.write({'state': 'draft'})
        return True

    def unlink(self):
        error_message = _('You cannot delete a record which is not in draft state')
        if self.user_has_groups('hr_employee_groups.main_admin_group'):
            return super(MissingAttendance, self).unlink()
        else:
            for rec in self:
                if rec.state not in ['draft']:
                    raise UserError(error_message)
                else:
                    return super(MissingAttendance, self).unlink()
