from odoo import http
from odoo.addons.web.controllers.main import content_disposition
from odoo.http import request

class EmpMissingAttXlsReports(http.Controller):

    @http.route('/web/employee_missing_attendance_xls_report/<int:id>', type='http', auth="user")
    def download_emp_missing_att_report_xls(self, id, **kw):

        data = request.env['attendance.request.report'].generate_missing_att_xls_report(id)
        filename = ' Employee Missing Attendance Sheet '
        if not data:
            return request.not_found()
        else:
            return request.make_response(data, [('Content-Type', 'application/octet-stream'),('Content-Disposition', content_disposition(filename + '.xlsx'))])
