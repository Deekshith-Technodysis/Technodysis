# -*- coding: utf-8 -*-

{
    'name': 'Invoice Customisations',
    'version': '14.0.1.0.1',
    "category": "Generic Modules/Invoice",
    'summary': 'Customisations for Invoice module',
    'description': 'Customisations for Invoice module',
    'author': 'Technodysis',
    'company': 'Technodysis',
    'maintainer': 'Technodysis',
    'website': 'https://www.technodysis.com',
    'depends': ['account','hr','web','employee_attendance_tracking','l10n_in'],
    'data': [
             'views/account_move_views.xml',
             'views/res_company_views.xml',
             'views/res_partner_bank_views.xml',
             'reports/report_layout.xml',
             'reports/report_invoice.xml',
             'reports/report_invoice_lumen.xml',
             'reports/report_invoice_questglobal.xml',
             'reports/report_invoice_sandvik.xml',
             'reports/report_invoice_accord_global.xml',
             'reports/account_report.xml',
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
