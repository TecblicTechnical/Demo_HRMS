# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request,content_disposition

class DownloadEmpXlsReports(http.Controller):

    @http.route('/web/employee_equipment_xlsx_report/<int:id>', type='http', auth="user")
    def download_emp_equipment_report_xls(self,id, **kw):
        data = request.env['equipment.asset.report'].generate_emp_asset_report(id)
        filename = 'Employee Asset Sheet'
        if not data:
            return request.not_found()
        else:
            return request.make_response(data, [('Content-Type', 'application/octet-stream'),('Content-Disposition', content_disposition(filename + '.xlsx'))])


    @http.route('/web/employee_asset_request_xlsx_report/<int:id>', type='http', auth="user")
    def download_emp_asset_request_report_xls(self,id, **kw):
        data = request.env['asset.request.report'].generate_emp_asset_request_report(id)
        filename = 'Employee Asset Request Sheet'
        if not data:
            return request.not_found()
        else:
            return request.make_response(data, [('Content-Type', 'application/octet-stream'),('Content-Disposition', content_disposition(filename + '.xlsx'))])


    @http.route('/web/employee_maintenance_request_xlsx_report/<int:id>', type='http', auth="user")
    def download_emp_maintenance_request_report_xls(self,id, **kw):
        data = request.env['asset.maintenance.request.report'].generate_emp_maintenance_request_report(id)
        filename = 'Employee Maintenance Request Sheet'
        if not data:
            return request.not_found()
        else:
            return request.make_response(data, [('Content-Type', 'application/octet-stream'),('Content-Disposition', content_disposition(filename + '.xlsx'))])
