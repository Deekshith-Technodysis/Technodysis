# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta
from odoo.exceptions import AccessError, UserError, ValidationError

class HrScreening(models.Model):
    _name = 'hr.screening'
    _description = "Screening"
    _order = "sequence desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(string="Applicant's Name",required=True,tracking=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    stage_id = fields.Selection([
        ('draft', 'Draft'),
        ('screened', 'Screened'),
        ('not_screened', 'Not Screened'),
        ('cancel', 'Cancel'),], 'Stages',default="draft",copy=False,tracking=True)
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

    _sql_constraints = [

    ('email_uniq', 'unique(email)', 'Email id is unique change your custom email id'),

    ('mobile_uniq','unique(mobile)','Phone number is unique so change your phone number')

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
    recruiter_id = fields.Many2one('hr.employee',string="Recruiter")
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

    application_status = fields.Selection(
            [('draft', 'Draft'),
             ('application_created', 'Application Created')], string='Application Status', readonly=True, copy=False, default='draft')


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
    

    def reset_screening(self):
        """ Reinsert the applicant into the recruitment pipe in the first stage"""
        for scr in self:
            scr.write(
                {'stage_id': 'draft',})

    def action_screen(self):
        for scr in self:
            # if scr.sequence == _('New'):
            #     self.sequence = self.env['ir.sequence'].next_by_code('hr.screening') or _('New')
            scr.write({'stage_id': 'screened'})

    def action_not_screen(self):
        for scr in self:
            # if scr.sequence == _('New'):
            #     self.sequence = self.env['ir.sequence'].next_by_code('hr.not.screening') or _('New')
            scr.write({'stage_id': 'not_screened'})

    def action_cancel(self):
        for scr in self:
            scr.write({'stage_id': 'cancel'})


    # def toggle_active(self):
    #     res = super(HrScreening, self).toggle_active()
    #     screening_active = self.filtered(lambda screening: screening.active)
    #     if screening_active:
    #         screening_active.reset_screening()
    #     screening_inactive = self.filtered(lambda screening: not screening.active)
    #     return res

    

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
        for application in self:
            name = str(application.sequence) + ' ' + str(application.name)
            result.append((application.id, name))
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

    