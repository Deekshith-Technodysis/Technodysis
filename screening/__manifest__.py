# -*- coding: utf-8 -*-

{
    'name': 'Screening',
    'version': '14.0.1.0.1',
    "category": "Generic Modules/Human Resources",
    'summary': 'Sourcing',
    'description': 'Sourcing',
    'author': 'Technodysis',
    'company': 'Technodysis',
    'maintainer': 'Technodysis',
    'website': 'https://www.technodysis.com',
    'depends': ['hr','contacts','hr_recruitment','hr_skills','sourcing'],
    'data': [
             'security/screening_security.xml',
             'security/ir.model.access.csv',
             'data/ir_sequence_data.xml',
             'views/hr_screening_views.xml',
             
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
