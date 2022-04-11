# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
import uuid
import base64
from werkzeug.urls import url_encode

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    invoice_id = fields.Many2one('account.move',string="Invoice Id",copy=False)
    invoice_count = fields.Integer(string='Invoice', compute='_invoice_count')

    def _invoice_count(self):
        for order in self:
            invoice_count = self.env['account.move'].search([('hr_employee_id', '=', order.id)])
            order.invoice_count = len(invoice_count)

    def hired_by_client(self):
        if self.invoice_id:
            raise UserError(_('Invoice is already generated for this employee. Kindly check it'))
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.client_work_address.id,
            'l10n_in_gst_treatment':self.client_work_address.l10n_in_gst_treatment,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'hr_employee_id':self.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': str(self.name) +'-'+str(self.emp_id),
                'quantity': 1.0,
            })],
        }
        account_move_obj = self.env['account.move'].create(invoice_vals)
        self.update({'invoice_id':account_move_obj.id,'active':False})