{
    'name': "Time Off Approval Flow",
    'summary': """Time Off Approval Flow""",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '16.0.1',
    'depends': ['base','hr','hr_holidays','hr_employee_groups'],
    'license': 'LGPL-3',
    'data': [
        'security/ir_rules.xml',
        'data/leave_request_to_manager.xml',
        'views/hr_leave.xml',
        'views/hr_allocation.xml',
        'views/menu.xml',
    ],
}
