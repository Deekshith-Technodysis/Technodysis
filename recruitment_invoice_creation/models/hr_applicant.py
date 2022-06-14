# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
import uuid
import base64
from werkzeug.urls import url_encode

class JobApplication(models.Model):
    _inherit = 'hr.applicant'

    create_invoice_bool = fields.Boolean(string="Create invoice",default=False,store=True,compute="fetch_job_type_create_invoice")
    invoice_id = fields.Many2one('account.move',string="Invoice Id",copy=False)
    is_invoiced = fields.Boolean(string="Invoice created",default=False,store=True,compute="_is_invoice_generated")

    @api.depends('invoice_id')
    def _is_invoice_generated(self):
        for line in self:
            if line.invoice_id:
                line.is_invoiced = True
            else:
                line.is_invoiced = False


    @api.depends('job_type_id')
    def fetch_job_type_create_invoice(self):
        for line in self:
            if line.job_type_id.enable_direct_invoice_creation:
                line.create_invoice_bool = True
            else:
                line.create_invoice_bool = False





    def create_invoice_action(self):
        if self.invoice_id:
            if self.invoice_id.state == 'draft':
                raise UserError(_('Invoice is already generated for this application. Kindly confim it'))
            if self.invoice_id.state == 'posted':
                raise UserError(_('Invoice %s , is already generated for this application.') % (self.invoice_id.name))
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))
        if self.salary_proposed <= 1:
            raise UserError(_('Salary Proposed for this application is %s. Kindly Update it') % (self.salary_proposed))
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.client_id.id,
            'l10n_in_gst_treatment':self.client_id.l10n_in_gst_treatment,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'job_type_id':self.job_type_id.id,
            'application_id':self.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': str(self.name) +'-'+str(self.partner_name),
                'quantity': 1.0,
                'pay_element':self.salary_proposed,
            })],
        }
        account_move_obj = self.env['account.move'].create(invoice_vals)
        self.update({'invoice_id':account_move_obj.id})