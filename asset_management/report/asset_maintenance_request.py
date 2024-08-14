from odoo import api, models, _
import datetime

class AssetMaintenanceRequestTmplReport(models.AbstractModel):
    _name = 'report.asset_management.asset_maintenance_request_report_tmpl'
    _description = 'Asset Maintenance Request Template'

    def _get_report_values(self, docids, data=None):
        record = self.env['asset.maintenance.request.report'].browse(docids)
        date_from_str = str(record.date_from)
        date_to_str = str(record.date_to)

        date_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d').date()
        date_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d').date()

        if record.employee_ids and (date_from and date_to):
            employee_ids = self.env['maintenance.request'].sudo().search([('employee_id','in', record.employee_ids.ids),('request_date', '>=', date_from),('request_date', '<=', date_to)])
        else:
            employee_ids = self.env['maintenance.request'].sudo().search([('request_date', '>=', date_from),('request_date', '<=', date_to)])

        data.update({
            'date_range': str(date_from) + ' to ' + str(date_to),
            'emp_maintenance_req_list': employee_ids
        })
        return {
            'data': data
        }
