from odoo import models, fields, api, _

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    seq_code = fields.Char("Company Seq Code")
