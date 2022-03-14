# -*- coding: utf-8 -*-

{
    'name': 'Sourcing',
    'version': '14.0.1.0.1',
    "category": "Generic Modules/Human Resources",
    'summary': 'Sourcing',
    'description': 'Sourcing',
    'author': 'Technodysis',
    'company': 'Technodysis',
    'maintainer': 'Technodysis',
    'website': 'https://www.technodysis.com',
    'depends': ['hr','contacts','employee_recruitment_customisation','hr_recruitment','hr_skills'],
    'data': [
             'security/sourcing_security.xml',
             'security/ir.model.access.csv',
             'data/ir_sequence_data.xml',
             'views/hr_employee_views.xml',
             'views/hr_work_location_views.xml',
             'views/hr_job_type_views.xml',
             'views/hr_applicant_views.xml',
             'views/hr_sourcing_views.xml',
             'wizard/sourcing_refuse_reason_views.xml',
             'wizard/sourcing_application_reason_views.xml',
             
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
