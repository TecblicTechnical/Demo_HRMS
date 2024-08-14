from odoo import models, fields, api, _

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    def remove_all_groups(self):
        # group_id = []
        for rec in self:
            rec.write({'groups_id': [(5,)]})
            internal_user_group = self.env.ref('base.group_user')
            rec.write({'groups_id': [(4, internal_user_group.id)]})
        return True