from odoo import api, models, _
import datetime

class JobApplicationTmplReport(models.AbstractModel):
    _name = 'report.recruitment_approval_flow.job_application_report_tmpl'
    _description = 'Report Recruitment Job Application'

    def _get_report_values(self, docids, data=None):
        record = self.env['job.application.report'].browse(docids)
        date_from_str = str(record.date_from)
        date_to_str = str(record.date_to)

        date_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d').date()
        date_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d').date()

        if date_from and date_to:
            application_ids = self.env['hr.applicant'].sudo().search([('create_date', '>=', date_from),('create_date', '<=', date_to)])

        data.update({
            'date_range': str(date_from) + ' to ' + str(date_to),
            'application_list': application_ids
        })
        return {
            'data': data
        }
