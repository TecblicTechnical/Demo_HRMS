# -*- coding: utf-8 -*-
{
    'name': "Recruitment Approval Flow",
    'summary': """Recruitment Approval Flow""",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '16.0.1',
    'depends': ['hr','hr_recruitment','hr_employee_groups'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'data/recruitment_mail_templates.xml',
        'report/job_application_report.xml',
        'report/job_position_report.xml',
        'views/recruitment_inherit.xml',
        'views/hr_applicant_inherit.xml',
        'wizard/job_applications_wizard.xml',
        'wizard/job_position_wizard.xml',
        'views/menus.xml',
    ],
}
