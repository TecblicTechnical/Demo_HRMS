from odoo import models, fields,api,_


class ResComapny(models.Model):
    _inherit = 'res.company'

    birthday_image = fields.Binary("Birthday Image")

