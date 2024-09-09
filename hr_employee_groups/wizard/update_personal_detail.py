from odoo import models, fields, api,_
from odoo.modules.module import get_module_resource
from odoo.exceptions import AccessError, UserError, ValidationError
import base64

class UpdatePersonalDetails(models.TransientModel):
    _name = 'update.personal.details'
    _description = 'Update Personal Details'

    @api.model
    def _default_image(self):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    employee_id = fields.Many2one('hr.employee', 'Employee')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country')
    email = fields.Char()
    phone = fields.Char()
    passport_id = fields.Char('Passport No')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    birthday = fields.Date('Date of Birth')
    emergency_contact = fields.Char("Emergency Contact")
    user_photo = fields.Image(default=_default_image)
    career_start_date = fields.Date('Career Start Date')

    @api.model
    def default_get(self, fields):
        res = super(UpdatePersonalDetails, self).default_get(fields)

        records = self.env['hr.employee.public'].browse(self.env.context.get('active_ids'))
        for rec in records:
            res.update({
                'user_photo': rec.image_1920,
                'street': rec.user_id.partner_id.street if rec.address_home_id else '',
                'street2': rec.user_id.partner_id.street2 if rec.address_home_id else '',
                'zip': rec.user_id.partner_id.zip if rec.address_home_id else '',
                'city': rec.user_id.partner_id.city if rec.address_home_id else '',
                'state_id': rec.user_id.partner_id.state_id if rec.address_home_id else '',
                'country_id': rec.user_id.partner_id.country_id if rec.address_home_id else '',
                'email': rec.personal_email_new if rec.personal_email_new else '',
                'phone': rec.user_id.partner_id.phone if rec.address_home_id else '',
                'passport_id': rec.passport_id,
                'gender': rec.gender,
                'birthday': rec.birthday,
                'emergency_contact': rec.emergency_contact,
                'career_start_date': rec.career_start_date,
            })

        return res

    def action_add_personal_details(self):
        if not self.env.context.get('active_id',False):
            raise UserError(_('Not Found Active Id !'))
        cur_emp_personal_details = False
        if self.env.context.get('active_id',False):
            for rec in self:
                employee = self.env['hr.employee.public'].sudo().search([('id','=', self.env.context.get('active_id'))])
                if employee:
                    employee.user_id.partner_id.write({
                        'street': rec.street,
                        'street2': rec.street2,
                        'zip': rec.zip,
                        'city': rec.city,
                        'state_id': rec.state_id.id,
                        'country_id': rec.country_id.id,
                        'phone': rec.phone,

                    })
                    employee.write({
                        'image_1920': rec.user_photo,
                        'address_home_id': employee.user_id.partner_id.id,
                        'passport_id': rec.passport_id,
                        'gender': rec.gender,
                        'birthday': rec.birthday,
                        'emergency_contact': rec.emergency_contact,
                        'career_start_date': rec.career_start_date,
                        'work_phone': rec.phone,
                        'personal_email_new': rec.email

                    })
                    # hr = self.env['res.users'].sudo().search([]).filtered(lambda a: a.has_group('hr_employee_groups.main_hr_group'))
                    # count = 1
                    # for i in hr:
                    #     print("i.........",i)
                    #     print("i.........",i.work_email)
                    #     if count == 1:
                    #         template_values = {
                    #             'email_to': 'admin.executive@tecblic.com',
                    #         }
                    #         template = self.env.ref('employee_attendance.employee_personal_details_approval_request_mail',raise_if_not_found=False)
                    #         template.sudo().write(template_values)
                    #         template.sudo().send_mail(cur_emp_personal_details.id, force_send=True)
                    #     count+=1

                    # mail = self.env['mail.mail'].sudo()
                    # mail_data = {'subject': 'Update Personal Detail',
                    #              'email_from': 'hr@tecblic.com',
                    #              'body_html': 'Dear ' + emp.name + ', <br/> Please note that you have a missing attendance for  ' + str(
                    #                  date_list) + '. <br/> Please get this regulairzed in the system through manager approval. <br/>'
                    #                               '<p> <a href="' + self.get_approval_url_for_action() + '" style = "height: 45px;width: 105px;background-color: #fd5b2a;padding: 10px;color: #fff;font-weight: 700;">Odoo</a></p>',
                    #              'email_to': emp.work_email}
                    # mail_out = mail.create(mail_data)
                    # mail.send(mail_out)
