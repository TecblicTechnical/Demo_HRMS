from odoo import api, models, fields,_,SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError
import datetime

class ApplicantInherit(models.Model):
    _inherit = "hr.applicant"

    # @api.depends('job_id')
    # def _compute_stage(self):
    #     for applicant in self:
    #         if applicant.job_id:
    #             stages = self.env['hr.recruitment.stage'].search([
    #                 ('job_ids', 'in', [applicant.job_id.id],('job_ids', '!=', False))
    #             ])
    #             applicant.stage_id = stages and stages[0] or False
    #         else:
    #             applicant.stage_id = False


    # @api.depends('job_id')
    # def _compute_stage(self):
    #     for applicant in self:
    #         if applicant.job_id:
    #             stages = self.env['hr.recruitment.stage'].search([
    #                 ('job_ids', 'in', [applicant.job_id.id]),
    #                 ('job_ids', '!=', False)
    #             ])
    #             if not stages:
    #                 raise ValidationError(
    #                     "No stage is available for the selected job, or the stages are not properly configured."
    #                 )
    #             applicant.stage_id = stages[0]
    #         else:
    #             applicant.stage_id = False

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        for rec in self:
            if rec.emp_id and rec.stage_id and not rec.stage_id.hired_stage:
                raise ValidationError(
                    "You cannot change the stage of an applicant who is already hired."
                )

    _sql_constraints = [
        ('unique_employee',
         'UNIQUE(partner_name, email_from)',
         'An applicant with the same name or email already exists.')
    ]

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id:
            return {
                'domain': {
                    'stage_id': [('job_ids', 'in', [self.job_id.id])]
                }
            }
        else:
            return {
                'domain': {
                    'stage_id': [('job_ids', '=', False)]
                }
            }

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        job_id = self._context.get('default_job_id')

        if job_id:
            search_domain = [('job_ids', 'in', [job_id])]
        else:
            search_domain = [('job_ids', '!=', False)]

        if domain:
            search_domain = [('id', 'in', stages.ids)] + search_domain
        else:
            search_domain = [('id', 'in', stages.ids)] + search_domain
        print("search_domain:::::::::", search_domain)
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)


    def create_employee_from_applicant(self):
        """ Create an employee from applicant """
        self.ensure_one()
        self._check_interviewer_access()
        if self.stage_id.name == 'Hired':
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
            raise UserError(_('Employee Can Create After Hired'))


    @api.model
    def create(self, vals):
        # First, call the super method to create the applicant
        applicant = super(ApplicantInherit, self).create(vals)

        job = applicant.job_id

        if job.state != 'approved':
            raise ValidationError(
                "You cannot create an applicant for a job that is not approved."
            )

        return applicant
