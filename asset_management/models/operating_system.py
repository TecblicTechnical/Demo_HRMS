from odoo import models, fields, api, _

class OperatingSystem(models.Model):
    _name = 'operating.system'
    _description = "Operating System"

    name = fields.Char("Name")


