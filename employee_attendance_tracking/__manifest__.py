# -*- coding: utf-8 -*-

{
    'name': 'Attendance Tracking',
    'version': '14.0.1.0.1',
    "category": "Generic Modules/Human Resources",
    'summary': 'Import Attendance of employees',
    'description': 'Import Attendance of employees',
    'author': 'Technodysis',
    'company': 'Technodysis',
    'maintainer': 'Technodysis',
    'website': 'https://www.technodysis.com',
    'depends': ['base','account','employee_recruitment_customisation'],
    'data': [
             'security/ir.model.access.csv',
             'views/attendance_tracking_views.xml',
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
