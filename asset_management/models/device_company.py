from odoo import models, fields, api, _

class DeviceCompany(models.Model):
    _name = 'device.company'
    _description = "Device Company"

    name = fields.Char("Name")
    device_code = fields.Char("Device Code")