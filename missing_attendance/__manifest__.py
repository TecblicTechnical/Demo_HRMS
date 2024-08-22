# -*- coding: utf-8 -*-
{
    'name': "Missing Attendance",
    'summary': """Missing Attendance""",
    'description': """Missing Attendance""",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Human Resources',
    'version': '16.0.1',
    'depends': ['base','hr','hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'security/rules.xml',
        'reports/report_details.xml',
        'reports/report.xml',
        'views/missing_attendance_views.xml',
        'views/my_attendance_views.xml',
        'views/res_company.xml',
        'wizard/attendance_report_wizard.xml',
    ],
}
