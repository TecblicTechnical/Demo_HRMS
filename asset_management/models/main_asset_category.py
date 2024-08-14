from odoo import models, fields, api, _

class MainAssetCategory(models.Model):
    _name = 'main.asset.category'
    _description = "Main Asset Category"

    name = fields.Char("Main Category")
