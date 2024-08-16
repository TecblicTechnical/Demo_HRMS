from odoo import api, models, fields,_,SUPERUSER_ID

class HrRecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    active = fields.Boolean("Active", index=True, default=True)
