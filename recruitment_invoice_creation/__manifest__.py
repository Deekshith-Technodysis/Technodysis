# -*- coding: utf-8 -*-

{
    'name': 'Invoice creation from Application',
    'version': '14.0.1.0.1',
    "category": "Generic Modules/Human Resources",
    'summary': 'Feature to enable invoice creation from application',
    'description': 'Feature to enable invoice creation from application',
    'author': 'Technodysis',
    'company': 'Technodysis',
    'maintainer': 'Technodysis',
    'website': 'https://www.technodysis.com',
    'depends': ['hr_recruitment','sourcing'],
    'data': [
    		 'views/hr_job_type.xml',
             'views/hr_applicant_views.xml',
             'views/account_move_views.xml',
             'views/hr_employee_views.xml',
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
