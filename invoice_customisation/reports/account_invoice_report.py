# -*- coding: utf-8 -*-

from odoo import models, fields, api

from functools import lru_cache


class ReportInvoiceBasic(models.AbstractModel):
    _name = 'report.account.report_invoice_basic'
    _description = 'Account report basic'
    _inherit = 'report.account.report_invoice'

    @api.model
    def _get_report_values(self, docids, data=None):
        rslt = super()._get_report_values(docids, data)
        rslt['report_type'] = data.get('report_type') if data else ''
        return rslt