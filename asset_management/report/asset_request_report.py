from odoo import api, models, _
import datetime

class AssetRequestTmplReport(models.AbstractModel):
    _name = 'report.asset_management.asset_request_report_tmpl'
    _description = 'Asset Request Template'

    def _get_report_values(self, docids, data=None):
        record = self.env['asset.request.report'].browse(docids)
        date_from_str = str(record.date_from)
        date_to_str = str(record.date_to)

        date_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d').date()
        date_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d').date()

        if record.employee_ids and (date_from and date_to):
            employee_ids = self.env['asset.request'].sudo().search([('employee_id','in', record.employee_ids.ids),('create_date', '>=', date_from),('create_date', '<=', date_to)])

        else:
            employee_ids = self.env['asset.request'].sudo().search([('create_date', '>=', date_from),('create_date', '<=', date_to)])


        data.update({
            'date_range': str(date_from) + ' to ' + str(date_to),
            'emp_asset_req_list': employee_ids
        })
        return {
            'data': data
        }
