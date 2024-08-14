from odoo import models, fields

class Generation(models.Model):
    _name = 'generation.generation'
    _description = "Generation"

    name = fields.Char("Name")