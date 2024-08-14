from odoo import http
from odoo.addons.web.controllers.main import content_disposition
from odoo.http import request

class EmpProbationXlsReports(http.Controller):

    @http.route('/web/employee_probation_sheet_report/<string:employee_period_type>', type='http', auth="user")
    def download_emp_probation_report_xls(self, employee_period_type, **kw):

        emp_probation_report_id = request.env['emp.probation.report']
        data = emp_probation_report_id.generate_emp_prob_report(employee_period_type)

        filename = ' Employee Probation Sheet '
        if not data:
            return request.not_found()
        else:
            return request.make_response(
        data, [('Content-Type', 'application/octet-stream'),('Content-Disposition', content_disposition(employee_period_type + filename + '.xlsx'))])


class EmpDetailXlsReports(http.Controller):

    @http.route('/web/employee_detail_sheet_report/<int:id>', type='http', auth="user")
    def download_emp_detail_report_xls(self,id, **kw):
        data = request.env['emp.detail.report'].generate_emp_detail_report(id)
        filename = ' Employee Sheet '
        if not data:
            return request.not_found()
        else:
            return request.make_response(
        data, [('Content-Type', 'application/octet-stream'),('Content-Disposition', content_disposition(filename + '.xlsx'))])
