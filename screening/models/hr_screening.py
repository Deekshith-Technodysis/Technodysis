# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta
from odoo.exceptions import AccessError, UserError, ValidationError

class HrScreening(models.Model):
    _name = 'hr.screening'
    _description = "Screening"
    _order = "sequence desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(string="Subject / Application Name")
    candidate_name = fields.Char(string="Applicant's Name",required=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    stage_id = fields.Selection([
        ('screened', 'Screened'),
        ('not_screened', 'Not Screened')], 'Stages',default="not_screened",copy=False,tracking=True)
    screening_date = fields.Date(string="Screening Date")
    sequence = fields.Char(string="Sequence",readonly=True, default=lambda self: _('New'), copy=False)
    category_id = fields.Many2many('hr.applicant.category',string="Category")
    currently_employed = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], 'Currently Working ?',default="no")

    applicant_skill_ids = fields.One2many('hr.employee.skill', 'screening_id', string="Skills")
    applicant_resume_line_ids = fields.One2many('hr.resume.line', 'screening_id', string="Resumé lines")
    job_type_id = fields.Many2one('hr.job.type',string="Job Type")
    client_id = fields.Many2one('res.partner',string="Client")
    mobile = fields.Char(string="Candidate's Mobile No.",required=True,tracking=True)
    email = fields.Char(string="Candidate's mail id",required=True,tracking=True)

    # _sql_constraints = [

    # ('email_uniq', 'unique(email)', 'Email id is unique change your custom email id'),

    # ('mobile_uniq','unique(mobile)','Phone number is unique so change your phone number')

    # ]

    _sql_constraints = [
        ('code_company_uniq', 'unique (email,company_id)', 'The code of the account must be unique per company !')
    ]

    

    total_exp_year = fields.Integer(string="Total Experience(Years)")
    total_exp_month = fields.Integer(string="Total Experience(Months)")
    relevant_exp_year = fields.Integer(string="Relevant Experience(Years)")
    relevant_exp_month = fields.Integer(string="Relevant Experience(Months)")
    hourly_salary_bool = fields.Boolean(string="Hourly salary calculation",default=False)

    amount_per_hour = fields.Float(string="Amount per hour")
    no_of_hours = fields.Float(string="Number of hours")
    total_amount = fields.Float(string="Total Amount",store=True,compute="fetch_total_amount")

    @api.depends('amount_per_hour','no_of_hours','hourly_salary_bool')
    def fetch_total_amount(self):
        for line in self:
            if line.hourly_salary_bool == True:
                line.total_amount = line.amount_per_hour * line.no_of_hours
            else:
                line.total_amount = 0



    
    notice_period_id = fields.Many2one('hr.applicant.notice.period',string="Notice Period")
    current_location = fields.Char(string="Current Location")
    preffered_location_id = fields.Many2many('hr.work.other.location','screening_loc_other_id',string="Open to work in Other location")
    other_offers_bool = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),('pipeline','Pipeline')], 'Other Offers')
    offer_price = fields.Float(string="Offer Price")
    joining_date = fields.Date(string="Tenative Joining Date")
    official_np_lwd = fields.Date(string="Official NP/ LWD")
    official_np_lwd_comments = fields.Text(string="Official NP/ LWD Comments")
    
    # Eduction and personal details
    degree_year_of_passing = fields.Char(string="Year of passing")
    university_name = fields.Char(string="University name")
    puc_passing_year = fields.Char(string="12 th Year of passing")
    puc_college_name = fields.Char(string="12th Name of the College")
    high_school_passing_year = fields.Char(string="10th Year of passing")
    school_name = fields.Char(string="Name of the school")
    work_gap_bool = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], "Gap in work")
    education_gap_bool = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')],"Gap Education")
    father_name = fields.Char(string="Father name")
    aadhar_no = fields.Char(string="Aadhar #")
    dob = fields.Date(string="Date of birth")

    # address
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")

    
    current_or_last_company = fields.Char(string="Current/Last Company")
    recruiter_id = fields.Many2one('hr.employee',string="Recruiter",required=True)
    lead_co_ordinator_id = fields.Many2one('hr.employee',string="Lead Recruiter")
    module_lead_id = fields.Many2one('hr.employee',string="Module Lead")
    ctc = fields.Float(string="CTC",tracking=True)
    ectc = fields.Float(string="ECTC",readonly=False,tracking=True)
    commission_percent = fields.Float("Commission Percent",tracking=True)
    training_bool = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], "Training")
    availability = fields.Datetime(string="Availability for Interview")
    change_reason = fields.Text(string="Reason for change",default="For career growth")
    selection_date = fields.Date(string="Date of selection")
    
    billing_rate = fields.Float(string="Billing Rate/Month",compute="compute_bill_rate")

    # Business Information
    lead_contact_id = fields.Many2one('res.partner',string="Spoc Contact Name")
    lead_contact_email = fields.Char(string="Spoc Email",related="lead_contact_id.email")
    lead_contact_number = fields.Char(string="Contact Number",related="lead_contact_id.mobile")
    talent_contact_id = fields.Many2one('res.partner',string="TA Contact Name")
    talent_contact_email = fields.Char(string="TA Email",related="talent_contact_id.email")
    talent_contact_number = fields.Char(string="Contact Number",related="talent_contact_id.mobile")
    jc_no = fields.Char(string="JC No.")
    contact_account = fields.Char(string="Account")
    business_unit = fields.Char(string="Business Unit")
    resume_no = fields.Char(string="Resume No", copy=False)



    enable_bill_rate = fields.Boolean(string="Enable Bill Rate",default=False,related="job_type_id.enable_bill_rate")

    sourcing_status = fields.Selection(
            [('draft', 'Draft'),
             ('sourcing_created', 'Sourcing Created')], string='Sourcing Status', readonly=True, copy=False, default='draft')
    screening_app_count = fields.Integer(string='Sourcing', compute='_sourcing_count')

    def _sourcing_count(self):
        for order in self:
            sourcing_count = self.env['hr.sourcing'].search([('origin_id', '=', order.id)])
            order.screening_app_count = len(sourcing_count)


    # onboarding status
    joining_status = fields.Selection([
        ('joined', 'Joined'),
        ('pending','Pending Joiner'),
        ('dropped', 'Dropped Out'),('op_dropped', 'Opportunity Dropped Out'),
        ('aborted', 'Aborted'),
        ('not_applicable','Not Applicable')], 'Joining Status',copy=False,default="not_applicable")
    jc_status = fields.Selection([
        ('available', 'JC Available'),
        ('not_available','JC Not Available'),
        ('not_applicable','Not Applicable')], 'JC Status',copy=False,default="not_applicable")
    offer_status = fields.Selection([
        ('offered', 'Offered'),
        ('in_progress','Offer in Progress'),
        ('accepted', 'Offer Accepted'),
        ('declined', 'Offer Declined'),
        ('aborted', 'Aborted'),
        ('not_applicable','Not Applicable')], 'Offer Status',copy=False,default="not_applicable")
    dnh_status = fields.Selection([
        ('submitted', 'Submitted'),
        ('pending', 'Pending for Submission'),('cleared','Cleared'),
        ('failed','Failed'),('in_progress','In Progress'),
        ('not_applicable','Not Applicable')], 'DNH Status',copy=False,default="not_applicable")
    wo_status = fields.Selection([
        ('approved', 'Approved'),
        ('in_progress','Approval in Progress'),
        ('not_initiated', 'Not Initiated'),
        ('not_applicable','FTE-Not Applicable')], 'WO Status',copy=False,default="not_applicable")
    bgv_status = fields.Selection([
        ('triggered', 'Triggered'),
        ('pending', 'Pending to Trigger'),
        ('not_applicable','Not Applicable')], 'BGV Status',copy=False,default="not_applicable")
    work_location_id = fields.Many2one('hr.work.location',string="Work Location")
    preferred_location = fields.Char(string="Preferred Location")
    expected_joining_date = fields.Date(string="Expected Joining Date",copy=False)
    study_field = fields.Many2one('hr.recruitment.degree',"Field of Study", tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('transender', 'Transgender'),
        ('dont_disclose','Dont want to disclose')
    ])
    alternate_phone = fields.Char(string="Alternate No",copy=False,default="0000000000")
    job_id = fields.Many2one('hr.job',string="Applied Job")
    department_id = fields.Many2one('hr.department',string="Department")
    offer_letter_type = fields.Selection([
        ('client', 'Client Employee'),
        ('internal', 'Internal Employee')
    ], string='Offer letter Type')


    active = fields.Boolean("Active", default=True, help="If the active field is set to false, it will allow you to hide the case without removing it.")
    

    def action_screen(self):
        for scr in self:
            scr.write({'stage_id': 'screened'})

    

    @api.onchange('screening_date')
    def updated_expected_joining_date(self):
        for line in self:
            if line.screening_date:
                line.expected_joining_date = line.screening_date + timedelta(days=20)


    @api.depends('ectc','ctc','commission_percent','client_id')
    def compute_bill_rate(self):
        for line in self:
            line.billing_rate = (((line.ectc * line.commission_percent)/100)+line.ectc)/12

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('hr.screening') or _('New')
        result = super(HrScreening, self).create(vals)
        return result

    def name_get(self):
        result = []
        for line in self:
            name = str(line.sequence) + ' ' + str(line.candidate_name)
            result.append((line.id, name))
        return result

    def create_application(self):
        for line in self:
            if not line.applicant_resume_line_ids:
                raise ValidationError(_("Please update Experience of candidate"))
            if not line.applicant_skill_ids:
                raise ValidationError(_("Please update Skills of candidate"))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Application'),
            'res_model': 'sourcing.application.reason',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sourcing_id': self.id},
            'views': [[False, 'form']]
        }

    def action_sourcing(self):
        sourcing_count = self.env['hr.sourcing']
        if not sourcing_count:
            categ_ids = [x.id for x in list(self.category_id)]
            preffered_location_ids = [x.id for x in list(self.preffered_location_id)]
            self.sourcing_status = 'sourcing_created'
            date = fields.Date.today()
            
            vals = {
                'origin_id': self.id,
                'name': self.name,
                'candidate_name':self.candidate_name,
                'category_id':[(6, 0, categ_ids)],
                'preffered_location_id':[(6, 0, preffered_location_ids)],
                'currently_employed':self.currently_employed,
                'applicant_skill_ids':[(6, 0, [skill.id for skill in self.applicant_skill_ids])],
                'applicant_resume_line_ids':[(6, 0, [skill.id for skill in self.applicant_resume_line_ids])],
                'job_type_id':self.job_type_id.id,
                'client_id':self.client_id.id,
                'mobile':self.mobile,
                'email':self.email,
                'total_exp_year':self.total_exp_year,
                'total_exp_month':self.total_exp_month,
                'relevant_exp_year':self.relevant_exp_year,
                'relevant_exp_month':self.relevant_exp_month,
                'hourly_salary_bool':self.hourly_salary_bool,
                'amount_per_hour':self.amount_per_hour,
                'no_of_hours':self.no_of_hours,
                'total_amount':self.total_amount,
                'notice_period_id':self.notice_period_id.id,
                'current_location':self.current_location,
                'preferred_location':self.preferred_location,
                'other_offers_bool':self.other_offers_bool,
                'offer_price':self.offer_price,
                'joining_date':self.joining_date,
                'official_np_lwd':self.official_np_lwd,
                'official_np_lwd_comments':self.official_np_lwd_comments,
                'degree_year_of_passing':self.degree_year_of_passing,
                'university_name':self.university_name,
                'puc_passing_year':self.puc_passing_year,
                'puc_college_name':self.puc_college_name,
                'high_school_passing_year':self.high_school_passing_year,
                'school_name':self.school_name,
                'work_gap_bool':self.work_gap_bool,
                'education_gap_bool':self.education_gap_bool,
                'father_name':self.father_name,
                'aadhar_no':self.aadhar_no,
                'dob':self.dob,
                'street':self.street,
                'street2':self.street2,
                'zip':self.zip,
                'city':self.city,
                'country_id':self.country_id.id,
                'state_id':self.state_id.id,
                'current_or_last_company':self.current_or_last_company,
                'recruiter_id':self.recruiter_id.id,
                'lead_co_ordinator_id':self.lead_co_ordinator_id.id,
                'module_lead_id':self.module_lead_id.id,
                'ectc':self.ectc,
                'ctc':self.ctc,
                'commission_percent':self.commission_percent,
                'training_bool':self.training_bool,
                'availability':self.availability,
                'change_reason':self.change_reason,
                'selection_date':self.selection_date,
                'lead_contact_id':self.lead_contact_id.id,
                'lead_contact_email':self.lead_contact_email,
                'lead_contact_number':self.lead_contact_number,
                'talent_contact_id':self.talent_contact_id.id,
                'talent_contact_email':self.talent_contact_email,
                'talent_contact_number':self.talent_contact_number,
                'jc_no':self.jc_no,
                'contact_account':self.contact_account,
                'business_unit':self.business_unit,
                'resume_no':self.resume_no,
                'sourcing_date':date,
                'joining_status':self.joining_status,
                'jc_status':self.jc_status,
                'offer_status':self.offer_status,
                'dnh_status':self.dnh_status,
                'wo_status':self.wo_status,
                'bgv_status':self.bgv_status,
                'work_location_id':self.work_location_id.id,
                'expected_joining_date':self.expected_joining_date,
                'study_field':self.study_field.id,
                'gender':self.gender,
                'alternate_phone':self.alternate_phone,
                'job_id':self.job_id.id,
                'department_id':self.department_id.id,
                'offer_letter_type':self.offer_letter_type,

            }
            source_obj = self.env['hr.sourcing'].create(vals)            
        else:
            if self.sourcing_status == 'sourcing_created':
                raise UserError(_("Sourcing already created, Please Check and Confirm your Sourcing Application"))
            else:
                raise UserError(_("Application already created, Please update the reasons and confirm the record"))



class HrSourcing(models.Model):
    _inherit = 'hr.sourcing'

    origin_id = fields.Many2one('hr.screening',string="Screening Id")