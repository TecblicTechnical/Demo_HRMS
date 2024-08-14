from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import ValidationError

class MaintenanceEquipmentInherit(models.Model):
    _inherit = 'maintenance.equipment'

    name = fields.Char('Company Equipment Name', required=True, translate=True)
    sequence = fields.Char(string='Asset Code')
    old_asset_code = fields.Char('Old Asset Code')
    emp_remark = fields.Char('Employee Remark')
    password_of_device = fields.Char(string='Password Of Device')
    b2b_company_id = fields.Many2one('res.partner', string='B2B Company',
                                     domain=lambda self: [('category_id', 'in', self.env.ref('asset_management.b2b_category_tag').id)])
    main_category = fields.Many2one('main.asset.category',related="category_id.main_category_id")
    equipment_state = fields.Selection([('damaged', 'Damaged'), ('working', 'Working')], string='Equipment State', required=True, default = 'working',compute='_compute_equipment_state',store=True)
    equipment_assign_to = fields.Selection(selection='_get_new_equipment_assign_to', string='Used By', required=True,default='employee')
    location = fields.Char('Location',default="Ahmedabad")
    hide_group_for_user = fields.Boolean('Hide for User')
    remove_selected_data = fields.Boolean(default=True, store=True)
    hard_copy_form_no = fields.Integer(string="Hard Copy Form No.")
    operating_system_id = fields.Many2one('operating.system',string='Operating System')
    state = fields.Selection([
        ('free', 'Free'),
        ('allocated', 'Allocated'),
        ('received_by_emp', 'Received By Employee'),
        ('damaged', 'Damaged')
    ], string='Status', default='free', tracking=True,compute='compute_working_state_or_department_or_employee')
    device_company = fields.Many2one('device.company', string='Device Company')
    warranty_period = fields.Selection([('1', '1 Year'),('2', '2 Year'),('3', '3 Year'),('4', '4 Year'),('5', '5 Year'),('6', '6 Year'),('7', '7 Year'),('8', '8 Year'),('9', '9 Year'),('10', '10 Year'),('11', '11 Year'),('12', '12 Year')],string='Warranty Period')
    ram = fields.Selection([('2', '2 GB'),('4', '4 GB'),('8', '8 GB'),('16', '16 GB'),('32', '32 GB'),('64', '64 GB'),('128', '128 GB'),('256', '256 GB')], string='Ram')
    is_mail_send = fields.Boolean('Is Mail Send',default=False)
    invoice_number = fields.Char(string="Invoice Number")
    invoice_date = fields.Date(string="Invoice Date")
    hsn = fields.Char(string="HSN Code")
    # vendor_id = fields.Many2one('res.partner', 'Vendor')
    processor_type = fields.Many2one('processor.type',string='Processor Type')
    device_generation = fields.Many2one('generation.generation',string='Generation')

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name))
        return result

    @api.depends('equipment_state', 'department_id', 'employee_id')
    def compute_working_state_or_department_or_employee(self):
        for rec in self:
            if rec.equipment_state == 'damaged':
                rec.state = 'damaged'
                rec.emp_remark = ''
                rec.department_id = False
                rec.employee_id = False

            elif rec.department_id or rec.employee_id:
                rec.state = 'allocated'
                rec.emp_remark = ''
            else:
                rec.state = 'free'
                rec.emp_remark = ''

    @api.model
    def _get_new_equipment_assign_to(self):
        selection = [
            ('department', 'Department'), ('employee', 'Employee')
        ]
        return selection

    @api.model
    def create(self, vals):
        equipment = super(MaintenanceEquipmentInherit, self).create(vals)
        for record in equipment:
            ######################## Track Id ########################

            today = datetime.today()
            year = today.strftime('%Y')
            month = today.strftime('%m')
            day = today.strftime('%d')
            b2b_company_name = record.b2b_company_id.seq_code if record.b2b_company_id else ''
            category_name = record.category_id.category_seq_code if record.category_id else ''
            sequence_code = 'maintenance.equipment.sequence'
            track_id_seq = self.env['ir.sequence'].next_by_code(sequence_code)
            record.sequence = f"{category_name}/AST/{month}{year}/{track_id_seq}"

            ######################## equipment state ########################
            if vals.get('employee_id') or vals.get('department_id'):
                record.state = 'allocated'

        if equipment.owner_user_id:
            equipment.message_subscribe(partner_ids=[equipment.owner_user_id.partner_id.id])

        return equipment

    def write(self, vals):
        if 'employee_id' in vals:
            vals['is_mail_send'] = False
            old_employee_id = self.employee_id.id
            old_employee = self.env['hr.employee'].browse(old_employee_id)
            if old_employee.user_id:
                self.message_unsubscribe(partner_ids=[old_employee.user_id.partner_id.id])

        equipment = super(MaintenanceEquipmentInherit, self).write(vals)

        if vals.get('owner_user_id'):
            self.message_subscribe(partner_ids=self.env['res.users'].browse(vals['owner_user_id']).partner_id.ids)

        return equipment

    @api.depends('maintenance_ids.stage_id')
    def _compute_equipment_state(self):
        for equipment in self:
            if any(request.stage_id.name == 'Scrap' for request in equipment.maintenance_ids):
                equipment.equipment_state = 'damaged'
                equipment.state = 'damaged'
            else:
                equipment.equipment_state = 'working'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(MaintenanceEquipmentInherit, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            equipment = self.env['maintenance.equipment'].search([])
            for rec in equipment:
                if not self.env.user.has_group('asset_management.asset_admin_group') :
                    rec.write({'hide_group_for_user': True})
                else:
                    rec.write({'hide_group_for_user': False})
        return res


    def free_allocated_asset(self):
        is_admin = self.env.user.has_group('asset_management.asset_admin_group')
        if is_admin:
            print("iffffffff")
            partner_ids= []
            for rec in self:
                employee_id = rec.employee_id
                if employee_id:
                    partner_ids.append(employee_id.user_id.partner_id.id)
                print("rec.........",rec)
                rec.employee_id = False
            rec.message_unsubscribe(partner_ids=partner_ids)

        else:
            raise ValidationError(_("Only Admin Can Free Asset...!"))


