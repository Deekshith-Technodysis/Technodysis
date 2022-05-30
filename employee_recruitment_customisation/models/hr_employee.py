# -*- coding:utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models,_


class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	signature = fields.Image('Signature', copy=False, attachment=True, max_width=1024, max_height=1024)
	emp_id = fields.Char(string="Employee id",required=True, copy=False, readonly=True, default=lambda self: _('New'))
	alternate_phone = fields.Char(string="Alternate No")
	is_billable = fields.Boolean(string="Is billable Candidate")
	client_work_address = fields.Many2one('res.partner',string="Client work address",tracking=True)

	# Current Address
	current_street = fields.Char()
	current_street2 = fields.Char()
	current_zip = fields.Char(change_default=True)
	current_city = fields.Char()
	current_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
	current_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

	# Employee Experience
	total_exp_year = fields.Integer(string="Total Experience(Years)")
	total_exp_month = fields.Integer(string="Total Experience")
	relevant_exp_year = fields.Integer(string="Relevant Experience(Years)")
	relevant_exp_month = fields.Integer(string="Relevant Experience")

	# Passport details
	passport_name = fields.Char(string="Name in the passport")
	passport_issue_date = fields.Date(string="Issue Date")
	passport_expiry_date = fields.Date(string="Expiry Date")
	passport_issue_country = fields.Many2one('res.country',string="Issuing Country")
	identification_id = fields.Char(string='Adhaar No.', groups="hr.group_hr_user", tracking=True)
	pan_no = fields.Char(string="PAN No")

	# CTC details
	salary_expected = fields.Float(string="Expected CTC (Rupees)",tracking=True)
	salary_proposed = fields.Float(string="Actual Salary",groups="hr.group_hr_user",tracking=True)

	enable_laptop_charges = fields.Boolean(string="Enable Laptop Charges ?",related="client_work_address.enable_laptop_charges")
	laptop_charges = fields.Float(string="Laptop Charges",tracking=True)

	enable_travel_expense = fields.Boolean(string="Enable Travel Expense ?",related="client_work_address.enable_travel_expense")
	travel_expense = fields.Float(string="Travel Expense",tracking=True)

	# Modifying standard fields
	gender = fields.Selection([
		('male', 'Male'),
		('female', 'Female'),
		('transender', 'Transgender'),
		('dont_disclose','Dont want to disclose')
	], groups="hr.group_hr_user", tracking=True)
	marital = fields.Selection([
		('single', 'Single'),
		('married', 'Married'),
		('widower', 'Widower'),
		('divorced', 'Divorced'),
		('dont_disclose','Dont want to disclose')
	], string='Marital Status', groups="hr.group_hr_user", default='single', tracking=True)
	certificate = fields.Selection([
		('graduate', 'Graduate'),
		('bachelor', 'Bachelor'),
		('master', 'Master'),
		('doctor', 'Doctor'),
		('other', 'Other'),
	], 'Highest Education', default='other', groups="hr.group_hr_user", tracking=True)
	father_name = fields.Char(string="Father's Name")
	joining_date = fields.Date(string="Joining Date",copy=False)
	internal_note = fields.Text(string="Internal Note",tracking=True)

	@api.model
	def create(self, vals):
		if vals.get('emp_id', _('New')) == _('New'):
			vals['emp_id'] = self.env['ir.sequence'].next_by_code('hr.employee') or _('New')
		result = super(HrEmployee, self).create(vals)
		return result

	@api.onchange('is_billable')
	def onchange_is_billable(self):
		if not self.is_billable:
			self.client_work_address = False

	@api.onchange('client_work_address')
	def onchange_client_work_address(self):
		for line in self:
			if line.client_work_address:
				if line.client_work_address.enable_laptop_charges == False:
					line.laptop_charges = False
				if line.client_work_address.enable_travel_expense == False:
					line.travel_expense = False



