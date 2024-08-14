{
    'name': "HR Employee",
    'summary': """HR Employee""",
    'author': "My Company",
    'license': 'LGPL-3',
    'website': "",
    'category': 'Uncategorized',
    'version': '16.0.1',
    'depends': ['base','hr','hr_timesheet'],
    'data': [
        'security/ir.model.access.csv',
        'security/user_groups.xml',
        'security/ir_rules.xml',
        'data/ir_cron.xml',
        'reports/employee_probation_templates.xml',
        'reports/employee_detail_report.xml',
        'views/hr_employee.xml',
        'views/hr_employee_public.xml',
        # 'wizard/update_personal_detail.xml',
        'wizard/emp_probation_report_wizard.xml',
        'wizard/employee_detail_report.xml',
    ],
}
# -*- coding: utf-8 -*-
