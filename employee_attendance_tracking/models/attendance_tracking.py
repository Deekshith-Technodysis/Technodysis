# -*- coding: utf-8 -*-

from odoo import api, fields, models, _



class AttendanceTracking(models.Model):
	_name = 'attendance.tracking'

	name = fields.Char(string="Name")
	emp_seq_id = fields.Char(string="Employee Id")
	emp_id = fields.Many2one('hr.employee',string="Employee",store=True,compute="fetch_emp_id")
	worked_days = fields.Float(string="Worked Days")
	leaves_taken = fields.Float(string="Leaves Taken")
	billed_days = fields.Float(string="Billed Days")
	billing_from = fields.Date(string="Billing from",required=True)
	billing_to = fields.Date(string="Billing to",required=True)
	no_of_weekends = fields.Float(string="Saturday/Sundays worked")
	total_hours_worked = fields.Float(string="Hours worked in Saturday/Sunday")
	charges = fields.Float(string="Charges per day")
	total_amount = fields.Float(string="Total amount to be paid",compute="compute_total_amount")
	company_id = fields.Many2one('res.company', store=True, readonly=True, default=lambda self: self.env.company)

	@api.depends('charges','total_hours_worked')
	def compute_total_amount(self):
		amount_per_hour = 0
		for line in self:
			amount_per_hour = line.charges/9
			line.total_amount = amount_per_hour * line.total_hours_worked

	
	@api.depends('emp_seq_id')
	def fetch_emp_id(self):
		for line in self:
			emp_id = self.env['hr.employee'].search([('emp_id','=',line.emp_seq_id)])
			if emp_id:
				for emp in emp_id:
					line.emp_id = emp.id
					line.name = emp.name

