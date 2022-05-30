# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import uuid
import base64
from werkzeug.urls import url_encode

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    invoice_id = fields.Many2one('account.move',string="Invoice Id",copy=False)
    invoice_count = fields.Integer(string='Invoice', compute='_invoice_count')
    client_hired_date = fields.Date(string="Hired by Client Date") 

    # SOW
    sow_start_date = fields.Date(string="Start Date")
    sow_end_date = fields.Date(string="End Date")
    sow_rate = fields.Date(string="Sow Rate")
    sow_ref = fields.Char(string="Sow Ref No.")
    notify_to = fields.Many2many('res.users','emp_user_ids',string="Notify To")

    sow_doc_ids = fields.One2many('sow.doc.line','sow_emp_id',string="Sow Line")

    @api.model
    def _cron_sow_notify(self):
        su_id =self.env['res.users'].search([('id','=',2)])
        date = datetime.date(datetime.today())
        var = date + relativedelta(months=+1)
        if su_id:
            for emp in self.env['hr.employee'].search([('sow_end_date', '=', var)]):
                template_id =  self.env['ir.model.data'].get_object_reference('recruitment_invoice_creation',
                                    'email_template_sow')[1]
                template_browse = self.env['mail.template'].browse(template_id)
                if template_browse:
                    for notify in emp.notify_to:
                        values = template_browse.generate_email(su_id.employee_id.id, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date','attachment_ids'])
                        values['email_from'] = su_id.partner_id.email
                        values['email_to'] = notify.employee_id.work_email
                        values['res_id'] = False
                        values['author_id'] = su_id.partner_id.id
                        values['body_html'] = (("Dear %s,<br/> \
                                                The SOW of the “%s”, is expiring on the date %s. Kindly renew the SOW.<br/>\
                                                Thanks")%(notify.employee_id.name,emp.name,emp.sow_end_date))
                        # author = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.id 
                        if not values['email_to'] and not values['email_from']:
                            pass
                        msg_id = self.env['mail.mail'].create({
                            'email_to': values['email_to'],
                            'auto_delete': True,
                            'email_from':values['email_from'],
                            'subject':values['subject'],
                            'body_html':values['body_html'],
                            'author_id':values['author_id']
                            })
                        mail_mail_obj = self.env['mail.mail']
                        if msg_id:
                            mail_mail_obj.sudo().send(msg_id)
            return True

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
        date = fields.Date.today()
        self.update({'invoice_id':account_move_obj.id,'active':False,'client_hired_date':date})


class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'
    _description = 'Departure Wizard'

    departure_reason = fields.Selection([
        ('fired', 'Terminated'),
        ('resigned', 'Resigned'),
        ('retired', 'Retired')
    ], string="Departure Reason", default="fired")

class SowDocLine(models.Model):
    _name = 'sow.doc.line'

    sow_emp_id = fields.Many2one('hr.employee',string="Emp Id")
    name = fields.Char(string="Doc Name")
    doc = fields.Binary(string="Document")