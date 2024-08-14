from odoo import models, fields, api, _

class MaintenanceEquipmentCategoryInherit(models.Model):
    _inherit = 'maintenance.equipment.category'

    main_category_id = fields.Many2one('main.asset.category',string="Main Category")
    category_seq_code = fields.Char("Category Seq Code")
    category_formula = fields.Char("Category Formula")