from odoo import api, models, fields,_
from odoo.exceptions import AccessError, UserError
import datetime

class ApplicantInherit(models.Model):
    _inherit = "hr.applicant"

    def create_employee_from_applicant(self):
        """ Create an employee from applicant """
        self.ensure_one()
        self._check_interviewer_access()
        if self.stage_id.name == 'Contract Signed':
            contact_name = False
            if self.partner_id:
                address_id = self.partner_id.address_get(['contact'])['contact']
                contact_name = self.partner_id.display_name
            # else:
            #     if not self.partner_name:
            #         raise UserError(_('You must define a Contact Name for this applicant.'))
            #     new_partner_id = self.env['res.partner'].create({
            #         'is_company': False,
            #         'type': 'private',
            #         'name': self.partner_name,
            #         'email': self.email_from,
            #         'phone': self.partner_phone,
            #         'mobile': self.partner_mobile
            #     })
            #     self.partner_id = new_partner_id
            #     address_id = new_partner_id.address_get(['contact'])['contact']
            employee_data = {
                'default_name': self.partner_name or contact_name,
                'default_job_id': self.job_id.id,
                'default_job_title': self.job_id.name,
                'default_joining_date': datetime.date.today(),
                'default_address_home_id': address_id,
                'default_department_id': self.department_id.id,
                'default_address_id': self.company_id.partner_id.id,
                'default_work_email': self.email_from,
                'default_work_phone': self.department_id.company_id.phone,
                'form_view_initial_mode': 'edit',
                'default_applicant_id': self.ids,
            }
            dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
            dict_act_window['context'] = employee_data
            return dict_act_window
        else:
            raise UserError(_('Employee Can Create After Contract Signed'))
