from odoo import models, fields

class HREmployeeDocument(models.Model):
    _name = 'hr.employee.document'
    _description = 'HR Employee Document'

    name = fields.Char("Document Name")
    document_name = fields.Char("Document Display Name")
    document_no = fields.Char("Document No.")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    document_files = fields.Binary(string="Document File", required=True, store=True)

