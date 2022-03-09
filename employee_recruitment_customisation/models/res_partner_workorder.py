# -*- coding: utf-8 -*-

import time
import json
import datetime
import io
from odoo import fields,api, models, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils

try:
	from odoo.tools.misc import xlsxwriter
except ImportError:
	import xlsxwriter

class ResPartnerWorkorder(models.Model):
	_name = 'res.partner.workorder'
	_description = "Workorder"

	name = fields.Char(string="Workorder No.",required=False, copy=False, readonly=False, default=lambda self: _('New'))
	client_id = fields.Many2one('res.partner',string="Client Name",required=False,domain="[('enable_wo','=',True)]")
	
	state = fields.Selection([
		('draft', 'Draft'),
		('waiting', 'Waiting'),
		('confirmed', 'Approved')
	], string='Status',copy=False,default='draft')

	new_workorder = fields.Boolean(string="New record",default=True)

	company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

	workorder_lines = fields.One2many('res.partner.workorder.line','workorder_id','Workorder Line')
	user_id = fields.Many2one('res.users',string="User id",default=lambda self: self.env.user)
	hr_id = fields.Many2one('res.partner', string="HR")


	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('res.partner.workorder') or _('New')
		result = super(ResPartnerWorkorder, self).create(vals)
		return result

	def update_workorder_list(self):
		if self.workorder_lines:
			for line in self:
				# lines are not updating properly need to check
				for lines in line.workorder_lines:
					applicant_id = self.env['hr.applicant'].search([('id','=',lines.applicant_id.id)])
					if applicant_id:
						for app in applicant_id:
							lines.update({
							'job_code':app.job_code,
							'contact_account':app.contact_account,
							'business_unit':app.business_unit,
							'vendor_id':app.company_id.id,
							'candidate_name':app.partner_name,
							'resume_number':app.resume_no,
							'total_exp_year':app.total_exp_year,
							'total_exp_month':app.total_exp_month,
							'employer_name':app.employer_name,
							'hike_percent':app.hike_percent,
							'salary_hike':app.salary_hike,
							'last_salary':app.last_salary,
							'currently_employed':app.currently_employed,
							'salary_expected':app.salary_proposed,
							'applicant_id':app.id,
							'client_id':app.client_id.id,
							'mark_up_percent':app.client_id.commission_percent,
							'relocation_needed':app.relocation_needed,
							'jc_exp_level':app.jc_exp_level.id,
							'expected_joining_date':app.expected_joining_date,
							'remarks':app.onboarding_remarks,
							'study_field':app.study_field.id,
							})
		self.update({'state':'waiting'})

	def generate_workorder_list(self):
		if self.workorder_lines:
			self.update({'state':'waiting','new_workorder':False})
		else:
			raise ValidationError("Kindly select the workorder lines")


	def action_workorder_send(self):
		''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
		self.ensure_one()
		template_id = self.env.ref('employee_recruitment_customisation.workorder_mail_template_id').id

		# report = self.env.ref('employee_recruitment_customisation.partner_wo_xlsx', False)

		# template_id = self._find_mail_template()
		template = self.env['mail.template'].browse(template_id)


		ctx = {
			'default_model': 'res.partner.workorder',
			'default_res_id': self.ids[0],
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'default_partner_ids':self.client_id.ids,
			'custom_layout': "mail.mail_notification_paynow",
			'force_email': True,
		}
		return {
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(False, 'form')],
			'view_id': False,
			'target': 'new',
			'context': ctx,
		}

	def update_records(self):
		date = fields.Date.today()
		for line in self.workorder_lines:
			line.applicant_id.update({'workorder_approval':date,'workorder_id':self.id})
		self.update({'state':'confirmed'})

	def reset_workorder(self):
		self.update({'state':'draft'})


class ResPartnerWorkorderLines(models.Model):
	_name = 'res.partner.workorder.line'

	workorder_id = fields.Many2one('res.partner.workorder')
	client_id = fields.Many2one('res.partner',string="Client Name",related="workorder_id.client_id",store=True)
	applicant_id = fields.Many2one('hr.applicant',string="Application",domain="[('stage_count_id','=','1'),'&',('workorder_approval','=',False),('client_id','=',client_id)]")
	job_code = fields.Char(string="Job Code")

	contact_account = fields.Char(string="Account")
	business_unit = fields.Char(string="Business Unit")
	
	mark_up_percent = fields.Float(strong="Mark-Up %")
	vendor_id = fields.Many2one('res.company',string="Vendor Name", required=False, default=lambda self: self.env.company)
	candidate_name = fields.Char(string="Candidate Name")
	resume_number = fields.Char(string="Resume number")
	total_exp_year = fields.Integer(string="Total Experience(Years)")
	total_exp_month = fields.Integer(string="Total Experience")

	employer_name = fields.Char(string="Current Employer Name")
	hike_percent = fields.Float(string="Last Hike Offered")
	salary_hike = fields.Date(string="Date of Last Salary Hike")
	last_salary = fields.Float(string="Last/ current Monthly drawn")

	salary_expected = fields.Float(string="Expected CTC by Candidate")

	current_hike_percent = fields.Float(string="Client % Hike Offered",digits=(16, 2),help="need to be calculated automatically",store=True,compute="_fetch_hike_wo_rate_value")
	monthly_wo_rate = fields.Float(string="Monthly WO rate",digits=(16,2),store=True,compute="_fetch_hike_wo_rate_value")
	remarks = fields.Text(string="Remarks")
	currently_employed = fields.Selection([
		('yes', 'Yes'),
		('no', 'No')], 'Currently employed',default="no")

	salary_expected_monthly = fields.Float(string="Expected CTC by Candidate Monthly",digits=(16, 2),store=True,compute="_fetch_salary")

	skill = fields.Char(string="Skill",compute="_fetch_skill",store=True)
	qualification = fields.Char(string="Highest Education",compute="_fetch_qualification",store=True)
	study_field = fields.Many2one('hr.recruitment.degree',"Field of Study", groups="hr.group_hr_user", tracking=True)
	relocation_needed = fields.Selection([
		('yes', 'Yes'),
		('no', 'No')], 'Relocation Needed ?',default="no")
	jc_exp_level = fields.Many2one('hr.applicant.exp.level',string="JC Exp. level")
	expected_joining_date = fields.Date(string="Expected Joining Date",copy=False)
	monthly_work_bill_rate = fields.Float(string="Monthly Billing rate",compute="_compute_bill_rate")


	@api.depends('last_salary','salary_expected','mark_up_percent')
	def _fetch_hike_wo_rate_value(self):
		for line in self:
			if line.salary_expected and line.last_salary:
				# line.current_hike_percent = ((line.salary_expected/12) - line.last_salary )/line.last_salary*100
				line.current_hike_percent = (line.applicant_id.salary_proposed - line.applicant_id.overall_ctc)/line.applicant_id.overall_ctc*100
				line.monthly_wo_rate = (line.current_hike_percent*line.mark_up_percent)/100

	@api.depends('applicant_id')
	def _fetch_skill(self):
		for line in self:
			line.skill = False
			if line.applicant_id:
				for lines in line.applicant_id.applicant_skill_ids:
					if lines.display_skill == True:
						if line.skill:
							line.skill = str(line.skill) +', '+ str(lines.skill_id.name)
						else:
							line.skill = str(lines.skill_id.name)


	@api.depends('applicant_id')
	def _fetch_qualification(self):
		for line in self:
			if line.applicant_id:
				line.qualification = line.applicant_id.certificate
				# for lines in line.applicant_id.applicant_resume_line_ids:
				# 	if lines.latest_qualification == True:
				# 		if line.qualification:
				# 			line.qualification = str(line.qualification) +', '+ str(lines.name)
				# 		else:
				# 			line.qualification = str(lines.name)



	@api.depends('salary_expected')
	def _fetch_salary(self):
		for line in self:
			if line.salary_expected:
				line.salary_expected_monthly = line.salary_expected/12

	@api.depends('applicant_id')
	def _compute_bill_rate(self):
		annual_salary = 0
		for line in self:
			# annual_salary = (line.applicant_id.salary_proposed+line.applicant_id.annual_variable_pay)* line.applicant_id.client_id.commission_percent/100
			# line.monthly_work_bill_rate = (line.applicant_id.salary_proposed + line.applicant_id.annual_variable_pay+annual_salary)/12
			# above formula changed 
			# 20% is fixed
			line.monthly_work_bill_rate = (line.applicant_id.salary_proposed +((line.applicant_id.salary_proposed*20)/100))/12

	@api.onchange('applicant_id')
	def _fetch_applicant_details(self):
		for line in self:
			if line.applicant_id:
				stage_id = self.env['hr.recruitment.stage'].search([('sequence','=',1)])
				if stage_id:
					for stage in stage_id:
						applicant_id = self.env['hr.applicant'].search([('id','=',self.applicant_id.id)])
						if applicant_id:
							for app in applicant_id:
								line.update({
									'workorder_id':self.id,
									'job_code':app.job_code,
									'contact_account':app.contact_account,
									'business_unit':app.business_unit,
									'vendor_id':app.company_id.id,
									'candidate_name':app.partner_name,
									'resume_number':app.resume_no,
									'total_exp_year':app.total_exp_year,
									'total_exp_month':app.total_exp_month,
									'employer_name':app.employer_name,
									'hike_percent':app.hike_percent,
									'salary_hike':app.salary_hike,
									'last_salary':app.last_salary,
									'currently_employed':app.currently_employed,
									# 'salary_expected':app.salary_expected,
									'salary_expected':app.salary_proposed,
									'client_id':app.client_id.id,
									'mark_up_percent':app.client_id.commission_percent,
									'relocation_needed':app.relocation_needed,
									'jc_exp_level':app.jc_exp_level.id,
									'expected_joining_date':app.expected_joining_date,
									'remarks':app.onboarding_remarks,
									'study_field':app.study_field.id,
									})
							line.workorder_id.write({'state':'waiting','new_workorder':False})





