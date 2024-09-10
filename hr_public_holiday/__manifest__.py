# -*- coding: utf-8 -*-
{
    'name': "HR Public Holidays",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Public Holiday List
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','hr_holidays','hr_employee_groups'],

    'data': [
        'security/ir.model.access.csv',
        'views/hr_public_holidays_view.xml',
    ],
    'demo': [
    ],
}
