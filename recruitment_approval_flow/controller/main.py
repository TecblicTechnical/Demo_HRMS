# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request,content_disposition

class RecruitmentDownloadEmpXlsReports(http.Controller):


    @http.route('/web/job_application_xlsx_report/<int:id>', type='http', auth="user")
    def download_job_application_xls_report(self,id, **kw):
        data = request.env['job.application.report'].generate_job_application_report(id)
        filename = 'Job Application Report'
        if not data:
            return request.not_found()
        else:
            return request.make_response(data, [('Content-Type', 'application/octet-stream'),('Content-Disposition', content_disposition(filename + '.xlsx'))])


    @http.route('/web/job_position_xlsx_report/<int:id>', type='http', auth="user")
    def download_job_position_xls_report(self,id, **kw):
        data = request.env['job.position.report'].generate_job_position_report(id)
        filename = 'Job Position Report'
        if not data:
            return request.not_found()
        else:
            return request.make_response(data, [('Content-Type', 'application/octet-stream'),('Content-Disposition', content_disposition(filename + '.xlsx'))])
