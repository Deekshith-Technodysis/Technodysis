# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from ast import literal_eval
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

class ResPartner(models.Model):
	_inherit = 'res.partner'

	is_client = fields.Boolean(string='Is a client', default=False,
		help="Check if the contact is a client")
	enable_wo = fields.Boolean(string="Enable Workorder",default=False,help="Check if workorder needs to be enabled")
	is_taf_status = fields.Boolean(string='Enable TAF Status', default=False,
		help="Check if the TAF Status has to be enabled")
	commission_percent = fields.Float(string="Commission(%)")
	inv_billing_type = fields.Selection([
		('mid_month', '21/22 days'),
		('full_month', '30/31 days')], 'Invoice Billing Type')

	enable_laptop_charges = fields.Boolean(string="Enable Laptop Charges ?",default=False)
	enable_travel_expense = fields.Boolean(string="Enable Travel Expense ?",default=False)
	enable_markup_value = fields.Boolean(string="Enable Markup Value ?",default=False)
	markup_value = fields.Float(string="Markup Value")

	hsn_no = fields.Char(string="HSN/SAC")
	pan_no = fields.Char(string="PAN")

	# MSA
	msa_start_date = fields.Date(string="Start Date")
	msa_end_date = fields.Date(string="End Date")
	notify_to = fields.Many2many('res.users','partner_user_ids',string="Notify To")

	msa_doc_ids = fields.One2many('msa.doc.line','msa_partner_id',string="MSA Lines")

	@api.model
	def _cron_msa_notify(self):
		su_id =self.env['res.users'].search([('id','=',2)])
		date = datetime.date(datetime.today())
		var = date + relativedelta(months=+1)
		if su_id:
			for partner in self.env['res.partner'].search([('msa_end_date', '=', var)]):
				template_id =  self.env['ir.model.data'].get_object_reference('employee_recruitment_customisation',
									'email_template_msa')[1]
				template_browse = self.env['mail.template'].browse(template_id)
				if template_browse:
					for notify in partner.notify_to:
						values = template_browse.generate_email(su_id.employee_id.id, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date','attachment_ids'])
						values['email_from'] = su_id.partner_id.email
						values['email_to'] = notify.employee_id.work_email
						values['res_id'] = False
						values['author_id'] = su_id.partner_id.id
						values['body_html'] = (("Dear %s,<br/> \
												The MSA of the “%s”, is expiring on the date %s. Kindly renew the MSA.<br/>\
												Thanks")%(notify.employee_id.name,partner.name,partner.msa_end_date))
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

	@api.onchange('enable_markup_value')
	def _update_markup_value(self):
		for line in self:
			if not line.enable_markup_value:
				line.markup_value = False




	@api.onchange('enable_wo','is_client','is_company')
	def _update_commission_percent(self):
		if not self.is_client:
			self.commission_percent = 0.0
		if not self.enable_wo:
			if self.is_company:
				self.update({'code':'company'})
			else:
				self.update({'code':'person'})
		else:
			self.update({'code':'client'})

	# Kanban fields
	color = fields.Integer('Color')
	code = fields.Selection([('company', 'Company'), ('client', 'Client'), ('person', 'Person')], 'Type of Contact')

	count_workorder_draft = fields.Integer(compute='_compute_workorder_count')
	count_workorder_confirmed = fields.Integer(compute='_compute_workorder_count')
	count_workorder = fields.Integer(compute='_compute_workorder_count')
	count_workorder_waiting = fields.Integer(compute='_compute_workorder_count')
	count_workorder_late = fields.Integer(compute='_compute_workorder_count')
	count_workorder_backorders = fields.Integer(compute='_compute_workorder_count')
	rate_picking_late = fields.Integer(compute='_compute_workorder_count')
	rate_picking_backorders = fields.Integer(compute='_compute_workorder_count')



	def _get_action(self, action_xmlid):
		action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
		# client_id = self.env['res.partner'].search([('enable_wo','=',True)])

		context = {
			'search_default_client_id': [self.id],
			'search_default_enable_wo': True,
			'default_client_id': self.id,
			'default_company_id': self.company_id.id,
		}

		action_context = literal_eval(action['context'])
		context = {**action_context, **context}
		action['context'] = context
		return action

	def _compute_workorder_count(self):
		# TDE TODO count can be done using previous two
		domains = {
			'count_workorder_draft': [('state', '=', 'draft')],
			'count_workorder_waiting': [('state', '=', 'waiting')],
			'count_workorder_confirmed': [('state', '=','confirmed')],
		}
		for field in domains:
			data = self.env['res.partner.workorder'].read_group(domains[field] +
				[('client_id', 'in', self.ids)],
				['client_id'], ['client_id'])
			count = {
				x['client_id'][0]: x['client_id_count']
				for x in data if x['client_id']
			}
			for record in self:
				record[field] = count.get(record.id, 0)

	
	def get_action_workorder_tree_waiting(self):
		return self._get_action('employee_recruitment_customisation.action_workorder_tree_waiting')

	def get_action_workorder_tree_confirmed(self):
		return self._get_action('employee_recruitment_customisation.action_workorder_tree_confirmed')
	

	def get_action_partner_tree_ready(self):
		return self._get_action('employee_recruitment_customisation.action_workorder_tree_draft')

	def get_action_partner_type(self):
		return self._get_action('employee_recruitment_customisation.res_action_partner')



class MsaDocLine(models.Model):
    _name = 'msa.doc.line'

    msa_partner_id = fields.Many2one('res.partner',string="Partner Id")
    name = fields.Char(string="Doc Name")
    doc = fields.Binary(string="Document")