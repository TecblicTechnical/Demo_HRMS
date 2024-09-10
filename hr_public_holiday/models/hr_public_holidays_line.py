from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrPublicHolidaysLine(models.Model):
    _name = 'hr.public.holidays.line'
    _description = 'Public Holidays Lines'
    _order = 'date, name desc'

    name = fields.Char('Name',required=True,)
    date = fields.Date('Date',required=True)
    year_id = fields.Many2one('hr.public.holidays','Calendar Year',required=True,ondelete='cascade',)
    variable_date = fields.Boolean('Date may change',default=True)
    state_ids = fields.Many2many('res.country.state','hr_holiday_public_state_rel','line_id','state_id','Related States')

    @api.constrains('date', 'state_ids')
    def _check_date_state(self):
        for line in self:
            line._check_date_state_one()

    def _check_date_state_one(self):
        if self.date.year != self.year_id.year:
            raise ValidationError(_(
                'Dates of holidays should be the same year as the calendar'
                ' year they are being assigned to'
            ))

        if self.state_ids:
            domain = [
                ('date', '=', self.date),
                ('year_id', '=', self.year_id.id),
                ('state_ids', '!=', False),
                ('id', '!=', self.id),
            ]
            holidays = self.search(domain)

            for holiday in holidays:

                if self.state_ids & holiday.state_ids:
                    raise ValidationError(_(
                        'You can\'t create duplicate public holiday per date'
                        ' %s and one of the country states.'
                    ) % self.date)
        domain = [('date', '=', self.date),
                  ('year_id', '=', self.year_id.id),
                  ('state_ids', '=', False)]
        if self.search_count(domain) > 1:
            raise ValidationError(_(
                'You can\'t create duplicate public holiday per date %s.'
            ) % self.date)
        return True
