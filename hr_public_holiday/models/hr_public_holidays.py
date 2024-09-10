from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrPublicHolidays(models.Model):
    _name = 'hr.public.holidays'
    _description = 'Public Holidays'
    _rec_name = 'year'
    _order = 'year'

    display_name = fields.Char('Name',compute='_compute_display_name',store=True,)
    year = fields.Integer('Calendar Year',required=True,default=date.today().year)
    country_id = fields.Many2one('res.country','Country')
    line_ids = fields.One2many('hr.public.holidays.line','year_id','Holiday Dates')

    @api.depends('year', 'country_id')
    def _compute_display_name(self):
        for line in self:
            if line.country_id:
                line.display_name = '%s (%s)' % (
                    line.year,
                    line.country_id.name
                )
            else:
                line.display_name = line.year

    @api.constrains('year', 'country_id')
    def _check_year_constrain(self):
        for line in self:
            line._check_year_only_once()

    def _check_year_only_once(self):
        if self.search_count([
                ('year', '=', self.year),
                ('country_id', '=', self.country_id.id),
                ('id', '!=', self.id)]):
            raise ValidationError(_(
                'You can not create duplicate public holiday per year and/or'
                ' country'
            ))
        return True


    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.display_name))
        return result



