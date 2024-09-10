# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request,content_disposition

class DownloadEmpLeaveXlsReports(http.Controller):

    @http.route('/web/employee_leave_request_xlsx_report/<int:id>', type='http', auth="user")
    def download_emp_maintenance_request_report_xls(self,id, **kw):
        data = request.env['employee.leave.request.report'].generate_emp_leave_request_report(id)
        filename = 'Employee Leaves'
        if not data:
            return request.not_found()
        else:
            return request.make_response(data, [('Content-Type', 'application/octet-stream'),('Content-Disposition', content_disposition(filename + '.xlsx'))])
