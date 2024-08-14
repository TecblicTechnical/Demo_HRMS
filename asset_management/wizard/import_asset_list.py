# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import binascii
from datetime import timedelta, datetime as dt, datetime
from dateutil import parser
import tempfile
import xlrd
from datetime import time as tm
from odoo.exceptions import ValidationError, UserError


class ImportAssetData(models.TransientModel):
    _name = 'import.asset.list'
    _description = 'Import Asset List'

    import_file = fields.Binary('Import File')

    def import_data(self):
        if self.import_file:
            return self.import_data_xlsx()
        else:
            raise ValidationError(_('Please Select the xlsx file'))

    def asset_excel_demo(self):
        print("asset excel demo")

    def import_data_xlsx(self):
        try:
            file_string = tempfile.NamedTemporaryFile(suffix=".xlsx")
            file_string.write(binascii.a2b_base64(self.import_file))
            book = xlrd.open_workbook(file_string.name)
            sheet = book.sheet_by_index(0)
        except:
            raise ValidationError(_("Please choose the correct file"))

        format1 = ['Old Asset Code','Company Equipment Name','Category','Company Name','Assigned To Employee','Assigned To Department','Assigned Date','Password','Operating System']
        # format2 = ['Asset Company Name','Category','Company','Assigned To Employee','Assigned To Department','Operating System','Assigned Date','Password']
        format2 = ['Asset Company Name', 'Category', 'B2B Company','Company Code', 'Employee', 'Department', 'Assign Date','Password','Device Company', 'Processor Type', 'Warranty', 'Generation','Ram','OS','Invoice Date']
        line = list(sheet.row_values(0))

        if line == format1:
            for i in range(1, sheet.nrows):
                line = list(sheet.row_values(i))

                equipment_assign_to = 'employee'
                date_value = line[6]
                if date_value:
                    assign_date = xlrd.xldate.xldate_as_datetime(date_value, book.datemode)
                else:
                    assign_date = None
                old_asset_code = line[0]
                company_equipment_name = line[1]
                category_name = line[2]
                company_name = line[3]
                employee_name = line[4]
                department_name = line[5]
                operating_system = line[8]
                assign_date = assign_date
                pass_of_device = line[7]

                if department_name:
                    equipment_assign_to = 'department'

                self._create_asset_data(company_equipment_name,category_name,company_name,employee_name,department_name,assign_date,pass_of_device,operating_system,equipment_assign_to,old_asset_code)

        elif line[0] == format2[0]:
            for i in range(1, sheet.nrows):
                line = list(sheet.row_values(i))

                equipment_assign_to = 'employee'
                date_value = line[6]
                assign_date = xlrd.xldate.xldate_as_datetime(date_value, book.datemode)
                invoice_dd = line[14]
                invoice_date = xlrd.xldate.xldate_as_datetime(invoice_dd, book.datemode)
                company_equipment_name = line[0]
                category_name = line[1]
                company_name = line[2]
                company_code = line[3]
                employee_name = line[4]
                department_name = line[5]
                assign_date = assign_date
                pass_of_device = line[7]
                device_company = line[8]
                processor_type = line[9]
                warranty = line[10]
                generation = int(line[11])
                ram_int = int(line[12])
                ram = str(ram_int)
                operating_system = line[13]
                invoice_date = invoice_date

                if department_name:
                    equipment_assign_to = 'department'

                self._create_asset_data(
                    company_equipment_name, category_name, company_name,company_code, employee_name,
                    department_name, assign_date,
                    pass_of_device, device_company, processor_type, warranty,
                    generation,ram,operating_system,invoice_date,equipment_assign_to
                )
        else:
            raise ValidationError(_("Please choose the correct format"))

    def _create_asset_data(self, company_equipment_name, category_name, company_name,company_code, employee_name,
                           department_name, assign_date,
                           pass_of_device, device_company,processor_type, warranty,
                           generation,ram,operating_system,invoice_date,equipment_assign_to, old_asset_code=''):

        category = self.env['maintenance.equipment.category'].search([('name', '=', category_name)], limit=1)
        if not category:
            category = self.env['maintenance.equipment.category'].create({'name': category_name})
        category_id = category.id if category else False

        company = self.env['res.partner'].search([('name', '=', company_name)], limit=1)
        if not company:
            company = self.env['res.partner'].create({'name': company_name,'seq_code':company_code, 'category_id': self.env.ref('asset_management.b2b_category_tag').ids})
        company_id = company.id if company else False

        employee = self.env['hr.employee'].search([('name', '=', employee_name)], limit=1)
        employee_id = employee.id if employee else False

        department = self.env['hr.department'].search([('name', '=', department_name)], limit=1)
        if not department and department_name != "":
            department = self.env['hr.department'].create({'name': department_name})
        department_id = department.id if department else False

        device_company_name = self.env['device.company'].search([('name', '=', device_company)], limit=1)
        if not device_company_name and device_company != "":
            device_company_name = self.env['device.company'].create({'name': device_company})
        device_company_id = device_company_name.id if device_company_name else False

        processor_type_name = self.env['processor.type'].search([('name', '=', processor_type)], limit=1)
        if not processor_type_name and processor_type != "":
            processor_type_name = self.env['processor.type'].create({'name': processor_type})
        processor_type_id = processor_type_name.id if processor_type_name else False

        generation_name = self.env['generation.generation'].search([('name', '=', generation)], limit=1)
        if not generation_name and generation != "":
            generation_name = self.env['generation.generation'].create({'name': generation})
        generation_id = generation_name.id if generation_name else False

        operating_system_id = self.env['operating.system'].search([('name', '=', operating_system)], limit=1)
        if not operating_system_id:
            operating_system_id = self.env['operating.system'].create({'name': operating_system})
        os_id = operating_system_id.id if operating_system_id else False

        existing_asset = self.env['maintenance.equipment'].search([('name', '=', company_equipment_name),('sequence', '=', old_asset_code)], limit=1)
        values = {
            'category_id': category_id,
            'b2b_company_id': company_id,
            'equipment_assign_to': equipment_assign_to,
            'operating_system_id': os_id,
            'assign_date': assign_date,
            'password_of_device': pass_of_device,
            'device_company': device_company_id,
            'processor_type': processor_type_id,
            'warranty_period': warranty,
            'device_generation': generation_id,
            'ram': ram,
            'invoice_date': invoice_date,
        }
        if employee_id:
            values.update({'employee_id':employee_id})
        if department_id:
            values.update({'department_id':department_id})
        if not existing_asset:
            if old_asset_code:
                values.update({
                    'name': company_equipment_name,
                    'sequence': old_asset_code,
                })
                self.env['maintenance.equipment'].with_context(import_file=1).create(values)
            else:
                values.update({
                    'name': company_equipment_name,
                })
                self.env['maintenance.equipment'].create(values)
        else:
            existing_asset.with_context(import_file=1).write(values)

