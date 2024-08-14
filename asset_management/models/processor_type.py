# -*- coding: utf-8 -*-
from odoo import models, fields

class ProcessorType(models.Model):
    _name = 'processor.type'
    _description = "Device Type"

    name = fields.Char("Name")


